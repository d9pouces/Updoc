# -*- coding: utf-8 -*-
from updoc.utils import strip_split

__author__ = 'flanker'

HOST = 'http://{BIND_ADDRESS}'
PUBLIC_BOOKMARKS = '1'
PUBLIC_BOOKMARKS_HELP = 'Are bookmarks publicly available?'
PUBLIC_PROXIES = '1'
PUBLIC_PROXIES_HELP = 'Is proxy.pac file publicly available?'
WS4REDIS_EMULATION_INTERVAL = 5000


# ELASTIC_SEARCH = {
#     'host': strip_split(ES_HOSTS),
#     'index': ES_INDEX,
#     'tika_extensions': set(strip_split(ES_TIKA_EXTENSIONS)),
#     'max_size': ES_MAX_SIZE,
#     'exclude_dir': set(strip_split(ES_EXCLUDED_DIR)),
#     'doc_type': ES_DOC_TYPE,
#     'plain_extensions': set(strip_split(ES_PLAIN_EXTENSIONS)),
# }

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

# Make this unique, and don't share it with anybody.
SECRET_KEY = '5I0zJQuHzqcACuzGIwTAC3cV6RlZpjV8MNUETYd5KZXg6UoI4G'

PIPELINE_JS = {
    'default': {
        'source_filenames': ('js/jquery.min.js', 'bootstrap3/js/bootstrap.min.js', 'js/djangofloor.js', 'js/ws4redis.js',
                             'js/jquery.ui.widget.js', 'js/jquery.iframe-transport.js', 'js/jquery.fileupload.js', ),
        'output_filename': 'js/default.js',
    },
    'ie9': {
        'source_filenames': ('js/html5shiv.js', 'js/respond.min.js',),
        'output_filename': 'js/ie9.js',
    }
}

if __name__ == '__main__':
    import doctest

    doctest.testmod()
