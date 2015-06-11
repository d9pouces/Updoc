# -*- coding: utf-8 -*-
from djangofloor.utils import DirectoryPath

__author__ = 'flanker'

HOST = 'http://{BIND_ADDRESS}'
PUBLIC_BOOKMARKS = '1'
PUBLIC_BOOKMARKS_HELP = 'Are bookmarks publicly available?'
PUBLIC_PROXIES = '1'
PUBLIC_PROXIES_HELP = 'Is proxy.pac file publicly available?'
PUBLIC_INDEX = '1'
PUBLIC_INDEX_HELP = 'Are documentations publicly available?'
PUBLIC_DOCS = '1'
PUBLIC_DOCS_HELP = 'Are documentations publicly available?'
WS4REDIS_EMULATION_INTERVAL = 5000

ES_HOSTS = 'localhost:9200'
ES_INDEX = 'updoc_index'
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
    'allauth.account.context_processors.account',
    'allauth.socialaccount.context_processors.socialaccount', ]

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
# CACHES = {
#     'default': {'BACKEND': 'django_redis.cache.RedisCache', 'LOCATION': 'redis://{REDIS_HOST}:{REDIS_PORT}/11',
#                 'OPTIONS': {'CLIENT_CLASS': 'django_redis.client.DefaultClient', 'PARSER_CLASS': 'redis.connection.HiredisParser', }, },
#     }

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

PIPELINE_JS = {
    'default': {
        'source_filenames': ('js/jquery.min.js', 'bootstrap3/js/bootstrap.min.js', 'js/djangofloor.js', 'js/ws4redis.js',
                             'js/jquery.ui.widget.js', 'js/jquery.iframe-transport.js', 'js/jquery.fileupload.js',
                             'js/fuelux.min.js', ),
        'output_filename': 'js/default.js',
    },
    'ie9': {
        'source_filenames': ('js/html5shiv.js', 'js/respond.min.js',),
        'output_filename': 'js/ie9.js',
    }
}
PIPELINE_CSS = {
    'default': {
        'source_filenames': ('bootstrap3/css/bootstrap.min.css', 'css/font-awesome.min.css',
                             'css/fuelux.min.css', 'css/djangofloor.css', ),
        'output_filename': 'css/default.css',
        'extra_context': {
            'media': 'all',
        },
    },
}

if __name__ == '__main__':
    import doctest

    doctest.testmod()
