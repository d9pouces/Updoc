# -*- coding: utf-8 -*-
"""
Define your custom middlewares in this file.
"""
import base64
from urllib.parse import unquote

from django.contrib import auth

__author__ = "flanker"


class GetAuthMiddleware(object):

    # noinspection PyMethodMayBeStatic
    def process_request(self, request):
        username = request.GET.get('username', '')
        password = request.GET.get('password', '')
        username = unquote(username)
        password = unquote(password)
        user = auth.authenticate(username=username, password=password)
        if user:
            request.user = user
            auth.login(request, user)
