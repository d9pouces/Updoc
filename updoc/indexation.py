# -*- coding: utf-8 -*-
"""all ElasticSearch-related functions are defined in this module.

"""
__author__ = 'flanker'

import base64
import codecs
import hashlib
import os
from django.conf import settings
import elasticsearch


def create_index():
    return []
    if not settings.ELASTIC_SEARCH['host']:
        return []
    host = settings.ELASTIC_SEARCH['host'][0]
    index = settings.ELASTIC_SEARCH['index']
    doc_type = settings.ELASTIC_SEARCH['doc_type']
    queries = []
    query = "curl -XPUT 'http://%s/%s/'" % (host, index)
    queries.append(query)
    query = "curl -XPUT 'http://%s/%s/%s/_mapping' -d" % (host, index, doc_type)
    query += '\'{"%s": {"properties": {"content": {"type": "attachment"}}}}\'' % doc_type
    queries.append(query)
    return queries


def index_archive(archive_id, root_path):
    return
    if not settings.ELASTIC_SEARCH['host']:
        return
    es = elasticsearch.Elasticsearch(settings.ELASTIC_SEARCH['host'])
    tika_extensions = settings.ELASTIC_SEARCH['tika_extensions']
    plain_extensions = settings.ELASTIC_SEARCH['plain_extensions']
    all_extensions = tika_extensions.union(plain_extensions)
    doc_type = settings.ELASTIC_SEARCH['doc_type']
    index = settings.ELASTIC_SEARCH['index']
    max_size = settings.ELASTIC_SEARCH['max_size']
    exclude_dir = settings.ELASTIC_SEARCH['exclude_dir']
    for (root, dirnames, filenames) in os.walk(root_path):
        dir_index = 0
        while dir_index < len(dirnames):
            if dirnames[dir_index] in exclude_dir:
                del dirnames[dir_index]
            else:
                dir_index += 1
        for filename in filenames:
            extension = filename.rpartition('.')[2]
            full_path = os.path.join(root, filename)
            if extension not in all_extensions or os.path.getsize(full_path) > max_size:
                continue
            value, content = '', ''
            if extension in plain_extensions:
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
            es.index(index=index, doc_type=doc_type, body=document, id=doc_id)


def delete_archive(archive_id):
    return
    if not settings.ELASTIC_SEARCH['host']:
        return
    es = elasticsearch.Elasticsearch(settings.ELASTIC_SEARCH['host'])
    doc_type = settings.ELASTIC_SEARCH['doc_type']
    index = settings.ELASTIC_SEARCH['index']
    es_query = {'query': {'term': {'archive_id': archive_id, }}, }
    es.delete_by_query(index=index, doc_type=doc_type, body=es_query)


def search_archive(query, archive_id=None, extension=None):
    """
    return a list of (UploadDoc.id, relpath) containing the query
    """
    return [], 0
    if not settings.ELASTIC_SEARCH['host']:
        return [], 0
    es = elasticsearch.Elasticsearch(settings.ELASTIC_SEARCH['host'])
    doc_type = settings.ELASTIC_SEARCH['doc_type']
    index = settings.ELASTIC_SEARCH['index']
    es_query = {'query': {'filtered': {'query': {'query_string': {'query': query, }},
                                       'filter': {}}}, 'size': 100,
                '_source': {'include': ['archive_id', 'path']}, }
    if archive_id:
        es_query['query']['filtered']['filter'].setdefault('term', {}).update({'archive_id': archive_id})
    if extension:
        es_query['query']['filtered']['filter'].setdefault('term', {}).update({'extension': extension})
    values = es.search(index=index, doc_type=doc_type, body=es_query)
    result_objs = []
    for hit in values.get('hits', {}).get('hits', []):
        result_objs.append((hit['_source']['archive_id'], hit['_source']['path']))
    return result_objs, values['hits']['total']

if __name__ == '__main__':
    import doctest

    doctest.testmod()
