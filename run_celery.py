#!/usr/bin/env python
# -*- coding: utf-8 -*-
from djangofloor.scripts import celery
import os
os.environ['DF_CONF_NAME'] = 'updoc-celery'
celery()
