# -*- coding: utf-8 -*-
"""
Define your custom middlewares in this file.
"""
import base64
from urllib.parse import unquote

from django.contrib import auth

__author__ = "flanker"


class BasicAuthMiddleware(object):

    # noinspection PyMethodMayBeStatic
    def process_request(self, request):
        if 'HTTP_AUTHORIZATION' in request.META:
            authentication = request.META['HTTP_AUTHORIZATION']
            (authmeth, auth_data) = authentication.split(' ', 1)
            if 'basic' == authmeth.lower():
                auth_data = base64.b64decode(auth_data.strip()).decode('utf-8')
                username, password = auth_data.split(':', 1)
                user = auth.authenticate(username=username, password=password)
                if user:
                    request.user = user
                    auth.login(request, user)


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
