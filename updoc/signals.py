# -*- coding: utf-8 -*-
import os
from django.conf import settings
from django.shortcuts import get_object_or_404
from django.template.loader import render_to_string
import shutil

from djangofloor.decorators import signal, is_authenticated, server_side
from djangofloor.tasks import scall, BROADCAST, SERVER, WINDOW, USER
from djangofloor.wsgi.window_info import render_to_string, WindowInfo

from updoc.models import RewrittenUrl, UploadDoc, Keyword
from updoc.process import process_uploaded_file
from django.utils.translation import ugettext as _

__author__ = 'Matthieu Gallet'


@signal(is_allowed_to=is_authenticated, path='updoc.delete_url_confirm')
def delete_url_confirm(window_info: WindowInfo, url_id: int):
    rewritten = get_object_or_404(RewrittenUrl.query(window_info), pk=url_id)
    template_values = {'src': rewritten.src, 'dst': rewritten.dst, 'url_id': url_id, }
    html = render_to_string('updoc/delete_url_confirm.html', template_values)
    scall(window_info, 'df.modal.show', to=[WINDOW], html=html)


@signal(is_allowed_to=is_authenticated, path='updoc.delete_doc_confirm')
def delete_doc_confirm(window_info: WindowInfo, doc_id: int):
    doc = get_object_or_404(UploadDoc.query(window_info), pk=doc_id)
    template_values = {'name': doc.name, 'doc_id': doc_id, }
    html = render_to_string('updoc/delete_doc_confirm.html', template_values)
    scall(window_info, 'df.modal.show', to=[WINDOW], html=html)


@signal(is_allowed_to=is_authenticated, path='updoc.edit_doc_name')
def edit_doc_name(window_info: WindowInfo, doc_id: int, name: str):
    UploadDoc.query(window_info).filter(pk=doc_id).update(name=name)


@signal(is_allowed_to=is_authenticated, path='updoc.edit_doc_keywords')
def edit_doc_keywords(window_info: WindowInfo, doc_id: int, keywords: str):
    doc = get_object_or_404(UploadDoc.query(window_info), pk=doc_id)
    doc.keywords.clear()
    for keyword in [x.strip() for x in keywords.lower().split() if x.strip()]:
        if keyword:
            doc.keywords.add(Keyword.get(keyword))


@signal(is_allowed_to=server_side, path='updoc.process_file', queue='slow')
def process_file(window_info: WindowInfo, doc_id: int, filename: str, original_filename: str):
    """
    * uncompress file if needed otherwise copy it
    * index its content
    * remove it

    Remove all if an error occurred

    :param window_info:
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
        doc = UploadDoc.query(window_info).get(pk=doc_id)
        destination_root = os.path.join(settings.MEDIA_ROOT, 'docs', doc.uid[0:2], doc.uid)
        process_uploaded_file(doc, temp_file, original_filename=original_filename, destination_root=destination_root)
        content = _('%(name)s has been uploaded and indexed') % {'name': doc.name}
        scall(window_info, 'df.notify', to=[USER], content=content,
              style='notification', level='info', timeout=5000)
    except Exception as e:
        if destination_root and os.path.isdir(destination_root):
            shutil.rmtree(destination_root)
        UploadDoc.query(window_info).filter(pk=doc_id).delete()
        if doc:
            content = _('An error happened during the processing of %(name)s: %(error)s') % \
                      {'name': doc.name, 'error': str(e)}
            scall(window_info, 'df.notify', to=[USER], content=content,
                  style='notification', level='error', timeout=7000)
        else:
            content = _('Unable to process query')
            scall(window_info, 'df.notify', to=[USER], content=content,
                  style='notification', level='error', timeout=7000)
    finally:
        if temp_file:
            temp_file.close()
        os.remove(filename)


@signal(is_allowed_to=server_side, path='updoc.delete_file', queue='slow')
def process_file(window_info: WindowInfo, doc_id: int):
    """
    :param window_info:
    :param doc_id:
    """
    for doc in UploadDoc.objects.filter(id=doc_id):
        doc.delete()
        content = _('%(name)s has been deleted') % {'name': doc.name}
        scall(window_info, 'df.notify', to=[USER], content=content,
              style='notification', level='info', timeout=7000)
        scall(window_info, 'updoc.delete_doc_info', to=[USER], doc_id=doc_id)
