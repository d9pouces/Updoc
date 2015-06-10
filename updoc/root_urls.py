# -*- coding: utf-8 -*-

from django.conf.urls import patterns, include, url
from updoc.feeds import LastDocsFeed, FavoritesFeed, KeywordFeed
from updoc.feeds import MostViewedDocsFeed

__author__ = 'flanker'

urls = [
    url(r'^rss/favorites/(?P<root_id>\d+)\.xml', FavoritesFeed(), name='favorites'),
    url(r'^rss/keywords/(?P<kw>[^/]+)\.xml', KeywordFeed(), name='keywords'),
    url(r'^rss/most_viewed\.xml', MostViewedDocsFeed(), name='most_viewed_feed'),
    url(r'^rss/last_docs\.xml', LastDocsFeed(), name='last_docs_rss'),
    url(r'^updoc/', include('updoc.urls')),
    url(r'^upload\.html$', 'updoc.views.upload'),
    url(r'^upload_doc_progress\.html$', 'updoc.views.upload_doc_progress'),
    url(r'^upload_api\.html', 'updoc.views.upload_doc_api'),
    ('^index$', 'updoc.views.index'),
]
