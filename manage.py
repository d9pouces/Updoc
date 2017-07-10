#!/usr/bin/env python
from djangofloor.scripts import django
import os
os.environ['DF_CONF_NAME'] = 'updoc-django'
django()
