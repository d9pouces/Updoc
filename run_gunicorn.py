#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import os
from djangofloor.scripts import aiohttp
os.environ['DF_CONF_NAME'] = 'updoc-aiohttp'
aiohttp()
