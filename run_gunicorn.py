#!/usr/bin/env python3
import os
from djangofloor.scripts import aiohttp
os.environ['DF_CONF_NAME'] = 'updoc-aiohttp'
aiohttp()
