# -*- coding: utf-8 -*-
from djangofloor.iniconf import OptionParser, bool_setting
__author__ = 'flanker'


def x_accel_converter(value):
    if bool_setting(value):
        return [('{MEDIA_ROOT}/', '{MEDIA_URL}'), ]
    return []


INI_MAPPING = [
    OptionParser('SERVER_NAME', 'global.server_name'),
    OptionParser('PROTOCOL', 'global.protocol'),
    OptionParser('BIND_ADDRESS', 'global.bind_address'),
    OptionParser('LOCAL_PATH', 'global.data_path'),
    OptionParser('ADMIN_EMAIL', 'global.admin_email'),
    OptionParser('TIME_ZONE', 'global.time_zone'),
    OptionParser('LANGUAGE_CODE', 'global.language_code'),
    OptionParser('USE_X_SEND_FILE', 'global.x_send_file', bool_setting),
    OptionParser('X_ACCEL_REDIRECT', 'global.x_accel_converter', x_accel_converter),
    OptionParser('FLOOR_AUTHENTICATION_HEADER', 'global.remote_user_header'),
    OptionParser('EXTRA_INSTALLED_APP', 'global.extra_app'),
    OptionParser('FLOOR_DEFAULT_GROUP_NAME', 'global.default_group'),

    OptionParser('PUBLIC_BOOKMARKS', 'global.public_bookmarks', bool_setting),
    OptionParser('PUBLIC_PROXIES', 'global.public_proxies', bool_setting),
    OptionParser('PUBLIC_INDEX', 'global.public_index', bool_setting),
    OptionParser('PUBLIC_DOCS', 'global.public_docs', bool_setting),

    OptionParser('ES_HOSTS', 'elasticsearch.hosts'),
    OptionParser('ES_INDEX', 'elasticsearch.index'),

    OptionParser('REDIS_HOST', 'redis.host'),
    OptionParser('REDIS_PORT', 'redis.port'),

    OptionParser('DATABASE_ENGINE', 'database.engine'),
    OptionParser('DATABASE_NAME', 'database.name'),
    OptionParser('DATABASE_USER', 'database.user'),
    OptionParser('DATABASE_PASSWORD', 'database.password'),
    OptionParser('DATABASE_HOST', 'database.host'),
    OptionParser('DATABASE_PORT', 'database.port'),

]
