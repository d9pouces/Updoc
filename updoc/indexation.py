# -*- coding: utf-8 -*-
"""all ElasticSearch-related functions are defined in this module.

"""
import functools
import base64
import codecs
import hashlib
import os
import elasticsearch
import requests
from elasticsearch import helpers
from django.conf import settings
from updoc.utils import strip_split

__author__ = 'Matthieu Gallet'


@functools.lru_cache()
def es_hosts():
    return strip_split(settings.ES_HOSTS)


@functools.lru_cache()
def es_tika_extensions():
    return set(strip_split(settings.ES_TIKA_EXTENSIONS))


@functools.lru_cache()
def es_plain_extensions():
    return set(strip_split(settings.ES_PLAIN_EXTENSIONS))


@functools.lru_cache()
def es_excluded_dir():
    return set(strip_split(settings.ES_EXCLUDED_DIR))


def create_index():
    if not es_hosts():
        return []
    host = es_hosts()[0]
    r1 = requests.put('http://%s/%s/' % (host, settings.ES_INDEX))
    r2 = None
    if r1.status_code == 200:
        data = '{"%s": {"properties": {"content": {"type": "attachment"}}}}' % settings.ES_DOC_TYPE
        r2 = requests.put('http://%s/%s/%s/_mapping' % (host, settings.ES_INDEX, settings.ES_DOC_TYPE), data=data)
    return r1, r2


def index_archive(archive_id, root_path):
    if not es_hosts():
        return
    es = elasticsearch.Elasticsearch(es_hosts())
    all_extensions = es_tika_extensions() | es_plain_extensions()
    excluded_dir = es_excluded_dir()
    for (root, dirnames, filenames) in os.walk(root_path):
        dir_index = 0
        while dir_index < len(dirnames):
            if dirnames[dir_index] in excluded_dir:
                del dirnames[dir_index]
            else:
                dir_index += 1
        for filename in filenames:
            extension = filename.rpartition('.')[2]
            full_path = os.path.join(root, filename)
            if extension not in all_extensions or os.path.getsize(full_path) > settings.ES_MAX_SIZE:
                continue
            value, content = '', ''
            if extension in es_plain_extensions():
                try:
                    with codecs.open(full_path, 'rb', encoding='utf-8') as fd:
                        value = fd.read()
                except UnicodeDecodeError:
                    pass
            if not value:
                with open(full_path, 'rb') as fd:
                    content = base64.b64encode(fd.read()).decode('ascii')
            relpath = os.path.relpath(full_path, root_path)
            doc_id = hashlib.sha1(('%d_%s' % (archive_id, relpath)).encode('utf-8')).hexdigest()
            document = {'archive_id': archive_id, 'path': relpath, 'content': content, 'value': value,
                        'name': os.path.basename(relpath), '_id': doc_id, 'extension': extension}
            es.index(index=settings.ES_INDEX, doc_type=settings.ES_DOC_TYPE, body=document, id=doc_id)


def delete_archive(archive_id):
    if not es_hosts():
        return
    es = elasticsearch.Elasticsearch(es_hosts())
    es_query = {'query': {'filtered': {'filter': {'term': {'archive_id': archive_id}}}},
                'size': 100000, '_source': {'include': ['archive_id', 'path']}, }
    values = es.search(index=settings.ES_INDEX, doc_type=settings.ES_DOC_TYPE, body=es_query)
    ids = [hit['_id'] for hit in values.get('hits', {}).get('hits', [])]
    if ids:
        actions = [{'delete': {'_id': id_}} for id_ in ids]
        helpers.bulk(es, actions, index=settings.ES_INDEX, refresh=True, doc_type=settings.ES_DOC_TYPE, stats_only=True)


def search_archive(query, archive_id=None, extension=None):
    """
    return a list of (UploadDoc.id, relpath) containing the query
    """
    if not es_hosts():
        return [], 0
    es = elasticsearch.Elasticsearch(es_hosts())
    es_query = {'query': {'filtered': {'query': {'query_string': {'query': query, }},
                                       'filter': {}}}, 'size': 100,
                '_source': {'include': ['archive_id', 'path']}, }
    if archive_id:
        es_query['query']['filtered']['filter'].setdefault('term', {}).update({'archive_id': archive_id})
    if extension:
        es_query['query']['filtered']['filter'].setdefault('term', {}).update({'extension': extension})
    values = es.search(index=settings.ES_INDEX, doc_type=settings.ES_DOC_TYPE, body=es_query)
    result_objs = [(hit['_source']['archive_id'], hit['_source']['path'])
                   for hit in values.get('hits', {}).get('hits', [])]
    return result_objs, values['hits']['total']


if __name__ == '__main__':
    import doctest

    doctest.testmod()
