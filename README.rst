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

    from constrictor import DPKGBuilder

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

    d = DPKGBuilder(output_directory, 'bbit-web-frontend', '1.5', 'all', dirs, links, maintainer_scripts)
    d.build_package()

Output file is named in the format *<packagename>_<version>_<architecture>.deb* and placed in the *destination_dir*. Alternatively, provide a name for your package as the *output_name* argument, and the package will be created with this name in the *output_directory*.

Known Issues
------------

- Lintian will complain about missing control file fields due to those not having the ability to be created (yet). For example copyright, changelog, extend-description, maintainer. Packages still install OK without these.
- Can't mark files as "config"
- As with any tar based archive, ownership of files based on uname/gname can be wrong if the user does not exist. Use with caution or create postinst scripts to fix.
