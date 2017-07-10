#!/usr/bin/env python3
from djangofloor.scripts import aiohttp, set_env

__author__ = 'Matthieu Gallet'

set_env(command_name='updoc-aiohttp')
aiohttp()
