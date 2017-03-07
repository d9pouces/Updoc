# -*- coding: utf-8 -*-
"""Setup file for the Updoc project.
"""

import codecs
import os.path
import re
import sys
from setuptools import setup, find_packages
__author__ = 'Matthieu Gallet'


commands = filter(lambda x: x[0:1] != '-', sys.argv)


# avoid a from pythonnest import __version__ as version
# (that compiles pythonnest.__init__ and is not compatible with bdist_deb)
version = None
for line in codecs.open(os.path.join('updoc', '__init__.py'), 'r', encoding='utf-8'):
    matcher = re.match(r"""^__version__\s*=\s*['"](.*)['"]\s*$""", line)
    version = version or matcher and matcher.group(1)

# get README content from README.md file
with codecs.open(os.path.join(os.path.dirname(__file__), 'README.md'), encoding='utf-8') as fd:
    long_description = fd.read()

entry_points = {
    'console_scripts': [
        'updoc-manage = djangofloor.scripts:django',
        'updoc-celery = djangofloor.scripts:celery',
        'updoc-aiohttp = djangofloor.scripts:aiohttp',
    ]
}

requirements = ['djangofloor>=1.0.0', 'elasticsearch>=2.0.0', 'requests', 'markdown']

setup(
    name='updoc',
    version=version,
    description='Upload HTML documentations and share bookmarks',
    long_description=long_description,
    author='Matthieu Gallet',
    author_email='github@19pouces.net',
    license='CeCILL-B',
    url='https://github.com/d9pouces/Updoc',
    entry_points=entry_points,
    packages=find_packages(),
    include_package_data=True,
    zip_safe=False,
    test_suite='updoc.tests',
    install_requires=requirements,
    setup_requires=[],
    classifiers=['Operating System :: POSIX :: BSD', 'Operating System :: POSIX :: Linux',
                 'Operating System :: Unix',
                 'License :: OSI Approved :: CEA CNRS Inria Logiciel Libre License, version 2.1 (CeCILL-2.1)',
                 'Programming Language :: Python :: 3.5', 'Programming Language :: Python :: 3 :: Only'],
)
