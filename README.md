# deb-constrictor


Build Debian Packages (.deb/DPKGs) natively in Python. No dependencies on Java, Ruby or other Debian packages.

Install
-------

Using pip:

    pip install deb-constrictor

Usage
-----

Define directories, links, scripts and dependencies:


```
from constrictor import DPKGBuilder, BinaryControl

dirs = [
    {
        'source': '~/python/beneboyit/frontend/src',
        'destination': '/srv/python/bbit-web-frontend',
        'uname': 'www-data'
    }
]

maintainer_scripts = {
    'postinst': '~/python/beneboyit/frontend/scripts/after-install',
    'preinst': '~/python/beneboyit/frontend/scripts/before-install'
}

links =  [
    {
        'source': '/etc/nginx/sites-enabled/bbit-web-frontend',
        'destination': '../sites-available/bbit-web-frontend'
    },
    {
        'source': '/etc/uwsgi/apps-enabled/bbit-web-frontend.ini',
        'destination': '../apps-available/bbit-web-frontend.ini'
    },
]

depends = ('nginx', 'uwsgi')

output_directory = '~/build'

c = BinaryControl('bbit-web-frontend',  '1.5', 'all', 'Ben Shaw', 'BBIT Web Frontend')

c.set_control_field('Depends', depends)

c.set_control_fields({'Section': 'misc', 'Priority': 'optional'})

d = DPKGBuilder(output_directory, c, dirs, links, maintainer_scripts)
d.build_package()
```

Output file is named in the format *<packagename>_<version>_<architecture>.deb* and placed in the *destination_dir*.
Alternatively, provide a name for your package as the *output_name* argument, and the package will be created with this
name in the *output_directory*.


constrictor-build tool
----------------------

constrictor-build is a command line tool that will build a package based on information in a JSON file. By default,
this file is in the current directory and called "build-config.json".

It loads the following fields and expects them to be in the same format as above:

* package (string, required)
* version  (string, required)
* architecture (string, required)
* maintainer (string, required)
* description (string, required)
* extra_control_fields (dictionary of standard DPKG control field pairs, optional)
* directories (array of dictionaries as per example above, optional)
* links (array of dictionaries as per example above, optional)
* maintainer_scripts (dictionary as per example above, optional)
* parent (string, optional, see parent section below)
* deb_constrictor (dictionary, optional, see deb_constrictor section below). Valid keys are:
    * ignore_paths (array of string, optional)

Examples of configuration files and how you might use constrictor-build in conjunction with other build steps are
included in the examples directory.

Environment variables in the form ${var_name} or $var_name will be substituted.

### parent ###

You can also provide a "parent" field, which is a path to another build JSON file (path is relative to the config file)
from which to read config values. For example, you might want to define the sections only in a parent config rather
than in each child config. The parent lookup is recursive so a parent can have a parent, and so on. constrictor-build
also attempts to load a base configuration file as the root of the configuration tree. The default location of this file
is *~/constrictor-build-config.json*, but can be overridden by setting the *CONSTRICTOR_BUILD_BASE_CONFIG_PATH*
environment variable.

Child values will replace parent values. Fields that are lists or dictionaries will be appended to/updated as
appropriate. Items in child configuration lists will not be added to the parent configuration if they already exists;
this means that if a parent and child both define the same Depends, or directory to include (for example), they won't be
included twice in the computer configuration,

For example, a parent with this configuration:

```
"extra_control_fields": {
    "Depends": ["some-package"]
}
```

Could be overridden with a child with this configuration:

```
"extra_control_fields": {
    "Depends": ["some-other-package"],
    "Provides": ["this-package"]
}
```

Creating a computed configuration like this:

```
"extra_control_fields": {
    "Depends": ["some-package", "some-other-package"],
    "Provides": ["this-package"]
}
```

### deb_constrictor  ##

Provide a dictionary of metadata to configure build options such as file exclusion, pre/post build actions or variables.
Valid keys are:
* ignore_paths (list of strings, optional)


#### ignore_paths ###

List of glob patterns of files to exclude when assembling data tar. Files are compared with their name relative to the
include dir, and have a leading slash.

For example, on the file system, you have directory layout like so:

- src
- src/media/
- src/media/123.jpg
- src/media/456.jpg

And your build-config.json specifies a directory with source *src/*. To exclude all the jpg files in the media directory,
set you ignore_paths to this:

`"ignore_paths": ["/media/*.jpg"]`

In this case though, the media directory will be empty (as it only contained .jpg files) and so would not be included in
the archive at all. This might not be desirable if you want an empty directory to be deployed.

The solution to this is to add a placeholder file in the directory that would otherwise be ignored - it should be called
either `.gitkeep` or `.depkeep`. If this file is found its containing directory will be added to the archive (as it is
not empty) however the placeholder file will not be included.


Known Issues
------------

- Can only make Binary packages
- Can't mark files as "config"
- As with any tar based archive, ownership of files based on uname/gname can be wrong if the user does not exist. Use
    with caution or create postinst scripts to fix.
