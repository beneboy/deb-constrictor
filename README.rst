===============
deb-constrictor
===============

Build Debian Packages (.deb/DPKGs) natively in Python.

Install
-------

Using pip::

    pip install deb-constrictor

Usage
-----

Define directories, links, scripts and dependencies::

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

Output file is named in the format *<packagename>_<version>_<architecture>.deb* and placed in the *destination_dir*. Alternatively, provide a name for your package as the *output_name* argument, and the package will be created with this name in the *output_directory*.


constrictor-build tool
----------------------

constrictor-build is a command line tool that will build a package based on information in a JSON file. By default, this file is in the current directory and called "build-config.json".

It loads the following fields and expects them to be in the same format as above:

- package (string, required)
- version  (string, required)
- architecture (string, required)
- maintainer (string, required)
- description (string, required)
- extra_control_fields (dictionary of standard DPKG control field pairs, optiona)
- directories (array of dictionaries as per example above, optiona)
- links (array of dictionaries as per example above, optiona)
- maintainer_scripts (dictionary as per example above, optiona)

You can also provide a "parent" field, which is a path to another build JSON file (path is relative to the config file) from which to read config values. For example, you might want to define the maintainer only in a parent config rather than in each child config.

Child values will replace parent values. "extra_control_fields" is not replaced as a whole, but the items in the child "extra_control_fields" will override those of the parents (i.e. they are merged with child items have precedence).

The parent lookup is recursive so a parent can have a parent, and so on.


Known Issues
------------

- Can only make Binary packages
- Lintian will complain about missing control file fields due to those not having the ability to be created (yet). For example copyright, changelog, extended-description. Packages still install OK without these.
- Can't mark files as "config"
- As with any tar based archive, ownership of files based on uname/gname can be wrong if the user does not exist. Use with caution or create postinst scripts to fix.
