# -*- coding: utf-8 -*-
from setuptools import setup, find_packages
from greatproject import __version__ as version
entry_points = {'console_scripts': ['greatproject-manage = djangofloor.scripts:manage',
                                    'greatproject-celery = djangofloor.scripts:celery',
                                    'greatproject-uswgi = djangofloor.scripts:uswgi',
                                    'greatproject-gunicorn = djangofloor.scripts:gunicorn']}
setup(
    name='greatproject',
    version=version,
    entry_points=entry_points,
    packages=find_packages(),
    install_requires=['djangofloor'],
)
