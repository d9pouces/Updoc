# -*- coding: utf-8 -*-
from django.conf.urls import url

from updoc.gravatar import views

__author__ = 'Matthieu Gallet'

urls = [
    url(r'^(?P<hashed>[a-f\d]{32})$', views.profile, name='profile'),
    url(r'^avatar/(?P<hashed>[a-f\d]{32})$', views.avatar, name='avatar'),
    url(r'^avatar/(?P<hashed>[a-f\d]{32})\.jpg$', views.avatar, name='avatar'),
]
