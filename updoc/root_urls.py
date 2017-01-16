# -*- coding: utf-8 -*-

from django.conf.urls import include, url

from updoc import views
from updoc.feeds import LastDocsFeed, FavoritesFeed, KeywordFeed, MostViewedDocsFeed

__author__ = 'Matthieu Gallet'

urls = [
    url(r'^rss/favorites/(?P<root_id>\d+)/', FavoritesFeed(), name='favorites'),
    url(r'^rss/keywords/(?P<kw>[^/]+)/', KeywordFeed(), name='keywords'),
    url(r'^rss/most_viewed/', MostViewedDocsFeed(), name='most_viewed_feed'),
    url(r'^rss/last_docs/', LastDocsFeed(), name='last_docs_rss'),
    url(r'^updoc/', include('updoc.urls', namespace='updoc')),
    url(r'^upload\.html$', views.upload, name='upload'),
    url(r'^upload_doc_progress\.html$', views.upload_doc_progress, name='upload_doc_progress'),
    url(r'^upload_api/', views.upload_doc_api, name='upload_doc_api'),
    # url('^index$', views.index, name='index'),
]
