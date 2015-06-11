# -*- coding: utf-8 -*-
from django.shortcuts import get_object_or_404
from django.template.loader import render_to_string

from djangofloor.decorators import connect, SignalRequest
from updoc.models import RewrittenUrl, UploadDoc, Keyword

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

if __name__ == '__main__':
    import doctest
    doctest.testmod()
