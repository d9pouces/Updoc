# -*- coding: utf-8 -*-
from djangofloor.conf.fields import BooleanConfigField, CharConfigField
from djangofloor.conf.mapping import SENDFILE_MAPPING, INI_MAPPING as DEFAULT

__author__ = 'Matthieu Gallet'


INI_MAPPING = DEFAULT + SENDFILE_MAPPING + [
    BooleanConfigField('global.public_bookmarks', 'PUBLIC_BOOKMARKS'),
    BooleanConfigField('global.public_proxies', 'PUBLIC_PROXIES'),
    BooleanConfigField('global.public_index', 'PUBLIC_INDEX'),
    BooleanConfigField('global.public_docs', 'PUBLIC_DOCS'),
    CharConfigField('elasticsearch.hosts', 'ES_HOSTS',
                    help_str='Comma-separated list of ElasticSearch servers.\n'
                             'ElasticSearch can be used to index all documents but remains optional.'
                             'Example: es-srv1.example.org:9200,es-srv2.example.org:9200'),
    CharConfigField('elasticsearch.index', 'ES_INDEX',
                    help_str='Name of the ElasticSearch index'),
]
