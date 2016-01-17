# -*- coding: utf-8 -*-
from djangofloor.iniconf import OptionParser, bool_setting, INI_MAPPING as DEFAULT
__author__ = 'Matthieu Gallet'


def x_accel_converter(value):
    if bool_setting(value):
        return [('{MEDIA_ROOT}/', '{MEDIA_URL}'), ]
    return []


INI_MAPPING = DEFAULT + [
    OptionParser('USE_X_SEND_FILE', 'global.x_send_file', bool_setting, doc_default_value=True),
    OptionParser('X_ACCEL_REDIRECT', 'global.x_accel_converter', x_accel_converter,
                 help_str='Nginx only. Set it to "true" or "false"', to_str=lambda x: 'True' if x else 'False'),
    OptionParser('PUBLIC_BOOKMARKS', 'global.public_bookmarks', bool_setting),
    OptionParser('PUBLIC_PROXIES', 'global.public_proxies', bool_setting),
    OptionParser('PUBLIC_INDEX', 'global.public_index', bool_setting),
    OptionParser('PUBLIC_DOCS', 'global.public_docs', bool_setting),
    OptionParser('ES_HOSTS', 'elasticsearch.hosts'),
    OptionParser('ES_INDEX', 'elasticsearch.index'),
    OptionParser('REDIS_HOST', 'redis.host'),
    OptionParser('REDIS_PORT', 'redis.port'),
    OptionParser('BROKER_DB', 'redis.broker_db', int),
    OptionParser('BIND_ADDRESS', 'global.bind_address', doc_default_value='localhost:8129'),
]
