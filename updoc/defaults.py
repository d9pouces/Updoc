# -*- coding: utf-8 -*-
import os
from djangofloor.utils import DirectoryPath

__author__ = 'Matthieu Gallet'
PROTOCOL = 'http'
HOST = '{PROTOCOL}://{SERVER_NAME}'
PUBLIC_BOOKMARKS = True
PUBLIC_BOOKMARKS_HELP = 'Are bookmarks publicly available?'
PUBLIC_PROXIES = True
PUBLIC_PROXIES_HELP = 'Is proxy.pac file publicly available?'
PUBLIC_INDEX = True
PUBLIC_INDEX_HELP = 'Is the list of all documentations publicly available?'
PUBLIC_DOCS = True
PUBLIC_DOCS_HELP = 'Are documentations publicly available?'
WS4REDIS_EMULATION_INTERVAL = 5000
LOCAL_PATH = os.path.join(os.path.dirname(__file__), '..', 'django_data')
BIND_ADDRESS = 'localhost:8129'
ES_HOSTS = 'localhost:9200'
ES_HOSTS_HELP = 'IP:port of your ElasticSearch database, leave it empty if you do not use ElasticSearch'
ES_INDEX = 'updoc_index'
ES_INDEX_HELP = 'name of your ElasticSearch index'
ES_TIKA_EXTENSIONS = 'pdf,html,doc,odt,rtf,epub'
ES_MAX_SIZE = 30 * 1024 * 1024
ES_DOC_TYPE = 'document'
ES_PLAIN_EXTENSIONS = 'txt,csv,md,rst'
ES_EXCLUDED_DIR = '_sources,_static'

TEMPLATE_CONTEXT_PROCESSORS = [
    'django.contrib.auth.context_processors.auth',
    'django.core.context_processors.debug',
    'django.core.context_processors.request',
    'django.core.context_processors.i18n',
    'django.core.context_processors.media',
    'django.core.context_processors.static',
    'django.core.context_processors.tz',
    'django.contrib.messages.context_processors.messages',
    'djangofloor.context_processors.context_base',
    'updoc.context_processors.most_checked',
    ]

# FLOOR_AUTHENTICATION_HEADER = None

########################################################################################################################
# sessions
########################################################################################################################
# SESSION_ENGINE = 'redis_sessions.session'
# SESSION_REDIS_PREFIX = 'session'
# SESSION_REDIS_HOST = '{REDIS_HOST}'
# SESSION_REDIS_PORT = '{REDIS_PORT}'
# SESSION_REDIS_DB = 10


########################################################################################################################
# caching
########################################################################################################################
CACHES = {
    'default': {'BACKEND': 'django_redis.cache.RedisCache', 'LOCATION': 'redis://{REDIS_HOST}:{REDIS_PORT}/11',
                'OPTIONS': {'CLIENT_CLASS': 'django_redis.client.DefaultClient',
                            'PARSER_CLASS': 'redis.connection.HiredisParser', }, },
    }

########################################################################################################################
# django-redis-websocket
########################################################################################################################

########################################################################################################################
# celery
########################################################################################################################
USE_CELERY = True
FLOOR_INSTALLED_APPS = ['updoc', ]
FLOOR_INDEX = 'updoc.views.index'
FLOOR_URL_CONF = 'updoc.root_urls.urls'
FLOOR_PROJECT_NAME = 'UpDoc!'
FILE_UPLOAD_TEMP_DIR = DirectoryPath('{LOCAL_PATH}/tmp')
# Make this unique, and don't share it with anybody.
SECRET_KEY = '5I0zJQuHzqcACuzGIwTAC3cV6RlZpjV8MNUETYd5KZXg6UoI4G'

FLOOR_EXTRA_JS = ['js/jquery.ui.widget.js', 'js/jquery.iframe-transport.js', 'js/jquery.fileupload.js',
                  'js/fuelux.min.js', 'js/updoc.js', ]
FLOOR_EXTRA_CSS = ['css/fuelux.min.css', ]
