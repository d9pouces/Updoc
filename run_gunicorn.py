#!/usr/bin/env python
# -*- coding: utf-8 -*-
import os
from djangofloor.scripts import gunicorn
os.environ['DF_CONF_NAME'] = 'updoc-gunicorn'
gunicorn()
