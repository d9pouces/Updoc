#!/usr/bin/env python
# -*- coding: utf-8 -*-
from djangofloor.scripts import django
import os
os.environ['DF_CONF_NAME'] = 'updoc-django'
django()
