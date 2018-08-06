# deb-constrictor


Build Debian Packages (.deb/DPKGs) natively in Python. No dependencies on Java, Ruby or other Debian packages.

Install
-------

Using pip:

    pip install deb-constrictor

Usage
-----

Define directories, links, scripts and dependencies:


```python
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
        'path': '/etc/nginx/sites-enabled/bbit-web-frontend',
        'target': '../sites-available/bbit-web-frontend'
    },
    {
        'path': '/etc/uwsgi/apps-enabled/bbit-web-frontend.ini',
        'target': '../apps-available/bbit-web-frontend.ini'
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
* configuration_files (array of strings, can be paths or globs to match multiple)
* maintainer_scripts (dictionary as per example above, optional)
* parent (string, optional, see parent section below)
* deb_constrictor (dictionary, optional, see deb_constrictor section below). Valid keys are:
    * ignore_paths (array of string, optional)
    * environment_variables (array of two-element arrays, optional)
    * variables (array of two-element arrays, optional)
    * commands (dictionary)
    

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

```json
{
  "extra_control_fields": {
      "Depends": ["some-package"]
  }
}
```

Could be overridden with a child with this configuration:

```json
{
  "extra_control_fields": {
      "Depends": ["some-other-package"],
      "Provides": ["this-package"]
  }
}
```

Creating a computed configuration like this:

```json
{
  "extra_control_fields": {
      "Depends": ["some-package", "some-other-package"],
      "Provides": ["this-package"]
  }
}
```

### deb_constrictor  ##

Provides a dictionary of metadata to configure build options such as file exclusion, pre/post build actions or variables.
Valid keys are:
* ignore_paths (array of strings, optional)
* environment_variables (array of two-element arrays, optional)
* variables (array of two-element arrays, optional)
* commands (dictionary of arrays, optional) 

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

#### environment_variables, variables ###

An array of two-element arrays in the format [key, value]; this format is used instead of a dictionary to preserve order so
that values may depend on values that have been defined earlier.

`environment_variables` and `variables` both behave in the same way in that any values they define can be used to 
interpolate variables throughout the configuration, however if calling external scripts (e.g. pre/post build scripts)
then only `environment_variables` will be passed to the sub-process.

Here's an example using variables.

```json
{
  "package": "${VENV_NAME}",
  "deb_constrictor": {
    "variables": [
      ["BUILD_DIR", "build"]
    ],
      "environment_variables": [
        ["PYTHON_VERSION", "3.6"],
        ["VENV_NAME", "example-virtualenv"],
        ["VENV_DIR", "${BUILD_DIR}/${VENV_NAME}"],
        ["VENV_BIN_DIR", "${VENV_DIR}/bin"]
      ]
  },
  "directories": [
    {
      "source": "${BUILD_DIR}/virtualenvs/${VENV_NAME}",
      "destination": "/var/virtualenvs/${VENV_NAME}"
    }
  ]
}
```

After the variables are interpolated the configuration will be like this:

```json
{
  "package": "example-virtualenv",
  "directories": [
    {
      "source": "build/virtualenvs/example-virtualenv",
      "destination": "/var/virtualenvs/example-virtualenv"
    }
  ]
}
```

Variable resolution order is `variables`, then `environment_variables`, then `os.environ`, i.e. a key will first be 
looked up in `variables`, if it does not exist then `environment_variables`, and so on to `os.environ`.

The `variables` values will only be used to interpolate the configuration while the `environment_variables` values will
be exported to any sub processes being called, so in this example, `PYTHON_VERSION`, `VENV_NAME`, `VENV_DIR` and 
`VENV_BIN_DIR` will be added to os.environ, while `BUILD_DIR` will not.

#### commands ###

Commands can be supplied to be run before and after building. For example, to setup a virtualenv for packaging, and to
upload the built .deb to an apt repository afterwards.

The supported keys for the commands are `prebuild` and `postbuild`, which will be called before and after (respectively)
the DPKG being created. The commands should be supplied as an array (as would be sent to `subprocess.call`).

When using parent config files, commands defined in children override those in parents (as opposed to appending).

Two special variables are set (in addition to other defined variables) which are interpolated into the commands and set
in the environment:

* `DEB_CONSTRICTOR_WORKING_DIR`: the directory containing the current config file being used (e.g. for 
_/foo/bar/build-config.json_, this value is _/foo/bar_) 
* `DEB_CONSTRICTOR_OUTPUT_PATH`: the output path of DPKG, relative to the cwd. This variable is only set for 
`postbuild`. This can be combined with the working dir path to get absolute path.

An example of using these:

```json
{
  "deb_constrictor": {
    "commands": {
      "prebuild": ["build-virtualenv.sh"],
      "postbuild": ["scp", "${DEB_CONSTRICTOR_OUTPUT_PATH}", "apt@apt-server.example.com/srv/apt/incoming/"]
    }
  }
}
```

The prebuild command `build-virtualenv.sh` has access to the `DEB_CONSTRICTOR_WORKING_DIR` environment variable (as well 
as other `environment_variables` that have been defined) and can refer to all of these to execute tasks.

This example shows that postbuild command that will be interpolated before being executed, so the actual command that is
called might be:

`scp build/example-1.0_amd64.deb apt@apt-server.example.com/srv/apt/incoming/`

#### remove_after_build ###

If `True`, then the DPKG will be deleted after building, or more specifically, after the `postbuild` command has been
run (it will be deleted even if a `postbuild` command does not exist though).

This is intended to be used to clean up a DPKG that is no longer needed, for example, if the `postbuild` script sends it
to a remote server.


Known Issues
------------

- Can only make Binary packages
- As with any tar based archive, ownership of files based on uname/gname can be wrong if the user does not exist. Use
    with caution or create postinst scripts to fix.
