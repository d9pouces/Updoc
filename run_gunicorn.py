#!/usr/bin/env python
# -*- coding: utf-8 -*-
import os
os.environ['DJANGOFLOOR_PROJECT_NAME'] = 'updoc'
from djangofloor.scripts import gunicorn
gunicorn()