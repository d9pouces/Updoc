# -*- coding: utf-8 -*-
from djangofloor.conf.fields import BooleanConfigField, CharConfigField, bool_setting, ConfigField
from djangofloor.conf.mapping import INI_MAPPING as DEFAULT

__author__ = 'Matthieu Gallet'


def x_accel_converter(value):
    if bool_setting(value):
        return [('{MEDIA_ROOT}/', '{MEDIA_URL}'), ]
    return []


INI_MAPPING = DEFAULT + [
    BooleanConfigField('global.x_send_file', 'USE_X_SEND_FILE', ),
    ConfigField('global.x_accel_converter', 'X_ACCEL_REDIRECT', from_str=x_accel_converter,
                to_str=lambda x: 'True' if x else 'False'),
    BooleanConfigField('global.public_bookmarks', 'PUBLIC_BOOKMARKS'),
    BooleanConfigField('global.public_proxies', 'PUBLIC_PROXIES'),
    BooleanConfigField('global.public_index', 'PUBLIC_INDEX'),
    BooleanConfigField('global.public_docs', 'PUBLIC_DOCS'),
    CharConfigField('elasticsearch.hosts', 'ES_HOSTS'),
    CharConfigField('elasticsearch.index', 'ES_INDEX'),
]
