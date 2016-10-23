import os
import re
import sys

from codecs import open

try:
    from setuptools import setup
except ImportError:
    from distutils.core import setup

if sys.argv[-1] == 'publish':
    os.system('python setup.py sdist upload')
    sys.exit()

packages = [
    'constrictor',
]

requires = []

with open('constrictor/__init__.py', 'r') as fd:
    version = re.search(r'^__version__\s*=\s*[\'"]([^\'"]*)[\'"]', fd.read(), re.MULTILINE).group(1)

if not version:
    raise RuntimeError('Cannot find version information')

with open('README.rst', 'r', 'utf-8') as f:
    readme = f.read()

setup(
    name='deb-constrictor',
    version=version,
    description='Build DPKGs natively with Python.',
    long_description=readme,
    author='Ben Shaw',
    author_email='ben@bbit.co.nz',
    url='https://github.com/beneboy/deb-constrictor',
    packages=packages,
    package_data={'': ['LICENSE']},
    scripts=['bin/constrictor-build'],
    package_dir={'constrictor': 'constrictor'},
    include_package_data=True,
    install_requires=requires,
    license='BSD 3-Clause',
    zip_safe=True,
    classifiers=(
        'Development Status :: 4 - Beta',
        'Intended Audience :: Developers',
        'Natural Language :: English',
        'License :: OSI Approved :: BSD License',
        'Programming Language :: Python',
        'Programming Language :: Python :: 2.7',
    )
)
