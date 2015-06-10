# -*- coding: utf-8 -*-
__author__ = 'flanker'

from django.conf.urls import patterns, url


urlpatterns = patterns(
    '',
    url(r'^show_alt/proxy\.pac$', 'updoc.views.show_proxies'),
    url(r'^favorite\.html', 'updoc.views.show_favorite'),
    url(r'^favorite/(?P<root_id>\d+).html$', 'updoc.views.show_favorite'),
    url(r'^my_docs\.html$', 'updoc.views.my_docs'),
    url(r'^delete_url/(?P<url_id>\d+)\.html$', 'updoc.views.delete_url'),
    url(r'^delete_doc/(?P<doc_id>\d+)\.html$', 'updoc.views.delete_doc'),
    url(r'^show/(?P<doc_id>\d+)/(?P<path>.*)$', 'updoc.views.show_doc'),
    url(r'^show_alt/(?P<doc_id>\d+)/(?P<path>.*)$', 'updoc.views.show_doc_alt'),
    url(r'^download/(?P<doc_id>\d+)\.(?P<fmt>zip|bz2|gz|xz)$', 'updoc.views.compress_archive'),
    url(r'^show_search_results\.html$', 'updoc.views.show_search_results'),
    url(r'^show_all_docs\.html$', 'updoc.views.show_all_docs'),
    # url(r'^edit/(?P<doc_id>\d+)/$', 'updoc.views.edit_doc'),
)
