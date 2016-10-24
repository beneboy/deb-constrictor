FIELD_BUILT_USING = "Built-Using"
FIELD_HOMEPAGE = "Homepage"
FIELD_DESCRIPTION = "Description"
FIELD_MAINTAINER = "Maintainer"
FIELD_INSTALLED_SIZE = "Installed-Size"
FIELD_PROVIDES = "Provides"
FIELD_CONFLICTS = "Conflicts"
FIELD_BREAKS = "Breaks"
FIELD_PRE_DEPENDS = "Pre-Depends"
FIELD_REPLACES = "Replaces"
FIELD_ENHANCES = "Enhances"
FIELD_SUGGESTS = "Suggests"
FIELD_RECOMMENDS = "Recommends"
FIELD_DEPENDS = "Depends"
FIELD_ESSENTIAL = "Essential"
FIELD_ARCHITECTURE = "Architecture"
FIELD_PRIORITY = "Priority"
FIELD_SECTION = "Section"
FIELD_VERSION = "Version"
FIELD_SOURCE = "Source"
FIELD_PACKAGE = "Package"

BINARY_CONTROL_ALLOWED_FIELDS = (
    FIELD_PACKAGE,
    FIELD_SOURCE,
    FIELD_VERSION,
    FIELD_SECTION,
    FIELD_PRIORITY,
    FIELD_ARCHITECTURE,
    FIELD_ESSENTIAL,
    FIELD_DEPENDS,
    FIELD_RECOMMENDS,
    FIELD_SUGGESTS,
    FIELD_ENHANCES,
    FIELD_REPLACES,
    FIELD_PRE_DEPENDS,
    FIELD_BREAKS,
    FIELD_CONFLICTS,
    FIELD_PROVIDES,
    FIELD_INSTALLED_SIZE,
    FIELD_MAINTAINER,
    FIELD_DESCRIPTION,
    FIELD_HOMEPAGE,
    FIELD_BUILT_USING
)

BINARY_CONTROL_REQUIRED_FIELDS = (FIELD_PACKAGE, FIELD_VERSION, FIELD_ARCHITECTURE, FIELD_MAINTAINER, FIELD_DESCRIPTION)

BINARY_DEPENDS_ET_AL_FIELDS = (FIELD_DEPENDS, FIELD_RECOMMENDS, FIELD_SUGGESTS, FIELD_ENHANCES, FIELD_PRE_DEPENDS,
                               FIELD_BREAKS, FIELD_CONFLICTS, FIELD_PROVIDES, FIELD_REPLACES)


class BinaryControl(object):
    def __init__(self, package, version, architecture, maintainer, description):
        self._control_fields = {
            FIELD_PACKAGE: package,
            FIELD_VERSION: version,
            FIELD_ARCHITECTURE: architecture,
            FIELD_MAINTAINER: maintainer,
            FIELD_DESCRIPTION: description
        }
        self.installed_size_bytes = None

    @staticmethod
    def format_field_value(field_name, field_value):
        if field_name in BINARY_DEPENDS_ET_AL_FIELDS:
            return ", ".join(field_value)

        return field_value

    def get_control_line(self, field_name):
        if field_name not in self._control_fields:
            raise KeyError("{} is not set.".format(field_name))

        field_value = self._control_fields[field_name]

        return "{}: {}".format(field_name, self.format_field_value(field_name, field_value))

    def set_control_field(self, field_name, field_value):
        if field_name not in BINARY_CONTROL_ALLOWED_FIELDS:
            raise KeyError("{} is not a valid field for a binary control file".format(field_name))

        self._control_fields[field_name] = field_value

    def set_control_fields(self, new_control_fields):
        for field_name, field_value in new_control_fields.items():
            self.set_control_field(field_name, field_value)

    def get_calculated_install_size_line(self):
        if self.installed_size_bytes is None:
            return None

        return '{}: {}'.format(FIELD_INSTALLED_SIZE, self.installed_size_bytes / 1024)

    def get_control_text(self):
        control_lines = []
        for field_name in BINARY_CONTROL_REQUIRED_FIELDS:
            control_lines.append(self.get_control_line(field_name))

        if FIELD_INSTALLED_SIZE not in self._control_fields:
            install_size_line = self.get_calculated_install_size_line()

            if install_size_line is not None:
                control_lines.append(install_size_line)

        for field_name in BINARY_CONTROL_ALLOWED_FIELDS:
            if field_name in BINARY_CONTROL_REQUIRED_FIELDS:
                continue

            if field_name not in self._control_fields:
                continue

            control_lines.append(self.get_control_line(field_name))

        return "\n".join(control_lines)


class DPKGControlOld(object):
    # some sensible defaults which could be overridden
    priority = "optional"

    def __init__(self, package_name, version, architecture, maintainer, section=None, description=None,
                 depends=None, installed_size_bytes=None):
        self.package_name = package_name
        self.version = version
        self.architecture = architecture
        self.maintainer = maintainer
        self.section = section
        self.description = description
        self.depends = depends
        self.installed_size_bytes = installed_size_bytes

    def get_control_text(self):
        control_text = ""
        control_text += "Package: {}\n".format(self.package_name)
        control_text += "Source: {}\n".format(self.package_name)
        control_text += "Maintainer: {}\n".format(self.maintainer)
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

        if self.section:
            control_text += "Section: {}\n".format(self.section)

        return control_text
