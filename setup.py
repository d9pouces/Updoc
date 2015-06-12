# -*- coding: utf-8 -*-
"""Setup file for the Updoc project.
"""

import codecs
import os.path

from setuptools import setup, find_packages
from updoc import __version__ as version


# get README content from README.md file
with codecs.open(os.path.join(os.path.dirname(__file__), 'README.md'), encoding='utf-8') as fd:
    long_description = fd.read()

entry_points = {
    'console_scripts': [
        'updoc-manage = djangofloor.scripts:manage',
        'updoc-celery = djangofloor.scripts:celery',
        'updoc-gunicorn = djangofloor.scripts:gunicorn',
    ]
}

requirements = ['djangofloor', 'elasticsearch', 'requests', 'gunicorn', 'markdown', 'hiredis', ]
try:
    # noinspection PyPackageRequirements
    import ipaddress
except ImportError:  # Python 3.3+
    ipaddress = None
    requirements.append('ipaddress')

setup(
    name='updoc',
    version=version,
    description='Upload HTML documentations and share bookmarks',
    long_description=long_description,
    author='flanker',
    author_email='flanker@19pouces.net',
    license='CeCILL-B',
    url='https://github.com/d9pouces/Updoc',
    entry_points=entry_points,
    packages=find_packages(),
    include_package_data=True,
    zip_safe=False,
    test_suite='updoc.tests',
    install_requires=requirements,
    setup_requires=[],
    classifiers=[
        'Programming Language :: Python',
        'Programming Language :: Python :: 3',
    ],
)
