# -*- coding: utf-8 -*-
from django.conf.urls import url
from updoc import views
__author__ = 'Matthieu Gallet'

urlpatterns = [
    url(r'^show_alt/proxy\.pac$', views.show_proxies, name='show_proxies'),
    url(r'^favorite\.html', views.show_favorite, name='show_favorite'),
    url(r'^favorite/(?P<root_id>\d+).html$', views.show_favorite, name='show_favorite'),
    url(r'^my_docs\.html$', views.my_docs, name='my_docs'),
    url(r'^delete_url/(?P<url_id>\d+)\.html$', views.delete_url, name='delete_url'),
    url(r'^delete_doc/(?P<doc_id>\d+)\.html$', views.delete_doc, name='delete_doc'),
    url(r'^show/(?P<doc_id>\d+)/(?P<path>.*)$', views.show_doc, name='show_doc'),
    url(r'^show_alt/(?P<doc_id>\d+)/(?P<path>.*)$', views.show_doc_alt, name='show_doc_alt'),
    url(r'^download/(?P<doc_id>\d+)\.(?P<fmt>zip|bz2|gz|xz)$', views.compress_archive, name='compress_archive'),
    url(r'^show_search_results\.html$', views.show_search_results, name='show_search_results'),
    url(r'^show_all_docs\.html$', views.show_all_docs, name='show_all_docs'),
    url(r'^docsets/docset-(?P<doc_id>\d+)/(?P<doc_name>.*)\.xml$', views.docset_feed, name='docset_feed'),
    url(r'^docsets/docset-(?P<doc_id>\d+)\.tgz$', views.docset, name='docset'),
    url(r'^docsets/docset-(?P<doc_id>\d+)\.tgz\.tarix$', views.docset_tarix, name='docset_tarix'),
    # url(r'^edit/(?P<doc_id>\d+)/$', 'updoc.views.edit_doc'),
]
