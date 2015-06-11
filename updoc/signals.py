# -*- coding: utf-8 -*-
import os
from django.conf import settings
from django.shortcuts import get_object_or_404
from django.template.loader import render_to_string
import shutil

from djangofloor.decorators import connect, SignalRequest
from djangofloor.tasks import call, SESSION
from updoc.models import RewrittenUrl, UploadDoc, Keyword
from updoc.process import process_uploaded_file
from django.utils.translation import ugettext as _

__author__ = 'flanker'


@connect(path='updoc.delete_url_confirm')
def delete_url_confirm(request: SignalRequest, url_id: int):
    rewritten = get_object_or_404(RewrittenUrl.query(request), pk=url_id)
    template_values = {'src': rewritten.src, 'dst': rewritten.dst, 'url_id': url_id, }
    html = render_to_string('updoc/delete_url_confirm.html', template_values)
    return [{'signal': 'df.modal.show', 'options': {'html': html, }, }]


@connect(path='updoc.delete_doc_confirm')
def delete_doc_confirm(request: SignalRequest, doc_id: int):
    doc = get_object_or_404(UploadDoc.query(request), pk=doc_id)
    template_values = {'name': doc.name, 'doc_id': doc_id, }
    html = render_to_string('updoc/delete_doc_confirm.html', template_values)
    return [{'signal': 'df.modal.show', 'options': {'html': html, }, }]


@connect(path='updoc.edit_doc_name')
def edit_doc_name(request: SignalRequest, doc_id: int, name: str):
    UploadDoc.query(request).filter(pk=doc_id).update(name=name)


@connect(path='updoc.edit_doc_keywords')
def edit_doc_keywords(request: SignalRequest, doc_id: int, keywords: str):
    doc = get_object_or_404(UploadDoc.query(request), pk=doc_id)
    doc.keywords.clear()
    for keyword in [x.strip() for x in keywords.lower().split() if x.strip()]:
        if keyword:
            doc.keywords.add(Keyword.get(keyword))


@connect(path='updoc.process_file', allow_from_client=False, delayed=True)
def process_file(request: SignalRequest, doc_id: int, filename: str, original_filename: str):
    """
    * uncompress file if needed otherwise copy it
    * index its content
    * remove it

    Remove all if an error occurred

    :param request:
    :param doc_id:
    :param filename:
    :param original_filename:
    """
    temp_file = None
    destination_root = None
    doc = None
    # noinspection PyBroadException
    try:
        temp_file = open(filename, 'rb')
        doc = UploadDoc.query(request).get(pk=doc_id)
        destination_root = os.path.join(settings.MEDIA_ROOT, 'docs', doc.uid[0:2], doc.uid)
        process_uploaded_file(doc, temp_file, original_filename=original_filename, destination_root=destination_root)
        call('df.messages.info', request, sharing=SESSION, html=_('%(name)s has been uploaded and indexed') % {'name': doc.name})
    except Exception as e:
        if destination_root and os.path.isdir(destination_root):
            shutil.rmtree(destination_root)
        UploadDoc.query(request).filter(pk=doc_id).delete()
        if doc:
            call('df.messages.error', request, sharing=SESSION, html=_('An error happened during the processing of %(name)s: %(error)s') % {'name': doc.name, 'error': str(e)})
        else:
            call('df.messages.error', request, sharing=SESSION, html=_('Unable to process query'))
    finally:
        if temp_file:
            temp_file.close()
        os.remove(filename)


@connect(path='updoc.delete_file', allow_from_client=False, delayed=True)
def process_file(request: SignalRequest, doc_id: int):
    """
    :param request:
    :param doc_id:
    """
    for doc in UploadDoc.objects.filter(id=doc_id):
        doc.delete()
        call('df.messages.info', request, sharing=SESSION, html=_('%(name)s has been deleted') % {'name': doc.name})

if __name__ == '__main__':
    import doctest
    doctest.testmod()
