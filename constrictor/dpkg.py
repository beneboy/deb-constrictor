import os
import os.path
from io import BytesIO
import tarfile
import tempfile
import time

from .ar import ARWriter
from .helpers import md5_for_path

MAINTAINER_SCRIPT_NAMES = ('preinst', 'postinst', 'prerm', 'postrm')
TAR_INFO_KEYS = ('uname', 'gname', 'uid', 'gid', 'mode')
DEBIAN_BINARY_VERSION = '2.0'
TAR_DEFAULT_MODE = 0o755
AR_DEFAULT_MODE = 0o644


class DPKGControl(object):
    # some sensible defaults which could be overridden
    priority = "optional"

    def __init__(self, package_name, version, architecture, section=None, description=None,
                 depends=None, installed_size_bytes=None):
        self.package_name = package_name
        self.version = version
        self.architecture = architecture
        self.section = section
        self.description = description
        self.depends = depends
        self.installed_size_bytes = installed_size_bytes

    def get_control_text(self):
        control_text = ""
        control_text += "Package: {}\n".format(self.package_name)
        control_text += "Source: {}\n".format(self.package_name)
        control_text += "Version: {}\n".format(self.version)
        control_text += "Architecture: {}\n".format(self.architecture)
        control_text += "Priority: {}\n".format(self.priority)
        if self.depends:
            depends_str = ', '.join(self.depends)
            control_text += "Depends: {}\n".format(depends_str)

        control_text += "Provides: {}\n".format(self.package_name)
        if self.installed_size_bytes is not None:
            control_text += "Installed-Size: {}\n".format(self.installed_size_bytes / 1024)
        control_text += "Description: {}\n".format(self.description or self.package_name)

        return control_text


def should_skip_file(file_name):
    if file_name in ('.DS_Store',):
        return True

    if file_name.endswith('.pyc'):
        return True

    return False


def generate_directories(path, existing_dirs=None):
    existing_dirs = existing_dirs or []
    dirname = os.path.dirname(path)

    if dirname == '.':
        return

    existing_dirs.append(dirname)
    generate_directories(dirname, existing_dirs)

    return existing_dirs


class DPKGBuilder(object):
    def __init__(self, output_directory, project_name, version, architecture, data_dirs, links, depends=None,
                 maintainer_scripts=None, output_name=None):
        self.output_directory = os.path.expanduser(output_directory)
        self.project_name = project_name
        self.version = version
        self.architecture = architecture
        self.data_dirs = data_dirs or []
        self.links = links or {}
        self.depends = depends
        self.maintainer_scripts = maintainer_scripts
        self.seen_data_dirs = set()
        self.working_dir = tempfile.mkdtemp()
        self.output_name = output_name or '{}_{}_{}.deb'.format(self.project_name, self.version, self.architecture)

    @staticmethod
    def list_data_dir(source_dir, dest_dir):
        for root_dir, dirs, files in os.walk(source_dir):
            for file_name in files:
                if should_skip_file(file_name):
                    continue
                file_path = os.path.join(root_dir, file_name)
                relative_path = file_path[len(source_dir):]
                yield dest_dir, file_path, relative_path

    def add_directory_root_to_archive(self, archive, dir_conf, file_path):
        for directory in reversed(generate_directories(file_path)):
            if directory in self.seen_data_dirs:
                continue

            dir_ti = tarfile.TarInfo()
            dir_ti.type = tarfile.DIRTYPE
            dir_ti.name = directory
            dir_ti.mtime = int(time.time())
            dir_ti.mode = TAR_DEFAULT_MODE
            self.filter_tar_info(dir_ti, dir_conf)
            archive.addfile(dir_ti)

            self.seen_data_dirs.add(directory)

    @staticmethod
    def filter_tar_info(tar_info, dir_conf):
        for tar_info_key in TAR_INFO_KEYS:
            if dir_conf.get(tar_info_key) is not None:
                setattr(tar_info, tar_info_key, dir_conf[tar_info_key])

        if 'uid' in dir_conf and 'uname' not in dir_conf:
            tar_info.uname = ''

        if 'gid' in dir_conf and 'gname' not in dir_conf:
            tar_info.gname = ''

        return tar_info

    @property
    def data_archive_path(self):
        return os.path.join(self.working_dir, 'data.tar.gz')

    def build_data_archive(self):
        data_tar_file = tarfile.open(self.data_archive_path, 'w:gz')

        file_size_bytes = 0

        file_md5s = []

        for dir_conf in self.data_dirs:
            source_dir = os.path.expanduser(dir_conf['source'])
            for dest_path_root, source_file_path, source_file_name in self.list_data_dir(source_dir,
                                                                                         dir_conf['destination']):
                if source_file_name.startswith('/'):
                    source_file_name = source_file_name[1:]
                archive_path = '.' + os.path.join(dest_path_root, source_file_name)

                self.add_directory_root_to_archive(data_tar_file, dir_conf, archive_path)

                file_size_bytes += os.path.getsize(source_file_path)
                file_md5s.append((md5_for_path(source_file_path), archive_path))
                data_tar_file.add(source_file_path, arcname=archive_path, recursive=False,
                                  filter=lambda ti: self.filter_tar_info(ti, dir_conf))

        for symlink_conf in self.links:
            symlink_dest = symlink_conf['destination']
            symlink_source = symlink_conf['source']

            if not symlink_source.startswith('.'):
                symlink_source = '.' + symlink_source

            self.add_directory_root_to_archive(data_tar_file, symlink_conf, symlink_source)
            link_ti = self.build_link_tarinfo(symlink_conf, symlink_dest, symlink_source)

            data_tar_file.addfile(link_ti)
            file_size_bytes += len(symlink_source)

        data_tar_file.close()

        return file_size_bytes, file_md5s

    def build_link_tarinfo(self, symlink_conf, symlink_dest, symlink_source):
        link_ti = tarfile.TarInfo()
        link_ti.type = tarfile.SYMTYPE
        link_ti.linkname = symlink_dest
        link_ti.name = symlink_source
        link_ti.mtime = int(time.time())
        link_ti = self.filter_tar_info(link_ti, symlink_conf)
        return link_ti

    @staticmethod
    def build_member_from_string(name, content):
        content_file = BytesIO(content)
        member = tarfile.TarInfo()
        member.type = tarfile.REGTYPE
        member.name = name
        member.mtime = int(time.time())
        member.uname = 'root'
        member.gname = 'root'
        member.size = len(content)
        return member, content_file

    @staticmethod
    def validate_maintainer_scripts(maintainer_scripts):
        for script_name in maintainer_scripts.keys():
            if script_name not in MAINTAINER_SCRIPT_NAMES:
                raise ValueError("Unknown maintainer script {}".format(script_name))

    @staticmethod
    def filter_maintainer_script_tar_info(tar_info):
        tar_info.uid = 0
        tar_info.gid = 0
        tar_info.mode = TAR_DEFAULT_MODE
        return tar_info

    @property
    def control_archive_path(self):
        return os.path.join(self.working_dir, 'control.tar.gz')

    def build_control_archive(self, control_data, file_md5s, maintainer_scripts):
        maintainer_scripts = maintainer_scripts or {}
        self.validate_maintainer_scripts(maintainer_scripts)

        control_tar = tarfile.open(self.control_archive_path, 'w:gz')

        for script_name, script_path in maintainer_scripts.items():
            control_tar.add(script_path, arcname=script_name, filter=self.filter_maintainer_script_tar_info)

        control_text = bytearray(control_data.get_control_text(), 'utf8')
        control_tar.addfile(*self.build_member_from_string('./control', control_text))

        md5sum_text = bytearray('\n'.join(['  '.join(md5_file_pair) for md5_file_pair in file_md5s]) + '\n', 'ascii')
        control_tar.addfile(*self.build_member_from_string('./md5sums', md5sum_text))
        control_tar.close()

    def assemble_deb_archive(self, control_archive_path, data_archive_path):
        pkg_path = os.path.join(self.output_directory, self.output_name)

        ar_writer = ARWriter(pkg_path)

        ar_writer.archive_text("debian-binary", "{}\n".format(DEBIAN_BINARY_VERSION), int(time.time()), 0, 0,
                               AR_DEFAULT_MODE)
        ar_writer.archive_file(control_archive_path, int(time.time()), 0, 0, AR_DEFAULT_MODE)
        ar_writer.archive_file(data_archive_path, int(time.time()), 0, 0, AR_DEFAULT_MODE)
        ar_writer.close()

        return pkg_path

    def build_package(self):
        file_size_bytes, file_md5s = self.build_data_archive()
        control = DPKGControl(self.project_name, self.version, self.architecture, depends=self.depends,
                              installed_size_bytes=file_size_bytes)
        self.build_control_archive(control, file_md5s, self.maintainer_scripts)

        return self.assemble_deb_archive(self.control_archive_path, self.data_archive_path)
