#!/usr/bin/env python
from djangofloor.scripts import celery
import os
os.environ['DF_CONF_NAME'] = 'updoc-celery'
celery()
