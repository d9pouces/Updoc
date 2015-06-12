# -*- coding: utf-8 -*-
from django.conf import settings

from updoc import __version__
from updoc.models import LastDocs

__author__ = 'flanker'


def most_checked(request):
    user = request.user if request.user.is_authenticated() else None
    most_checked_ = LastDocs.query(request).select_related('doc').order_by('-count')[0:5]
    if not settings.PUBLIC_INDEX and user is None:
        most_checked_ = []
    return {'updoc_most_checked': most_checked_, 'updoc_version': __version__}
