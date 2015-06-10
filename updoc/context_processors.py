# -*- coding: utf-8 -*-
from django.conf import settings
from updoc.models import LastDocs
from updoc.utils import bool_settings

__author__ = 'flanker'


def most_checked(request):
    user = request.user if request.user.is_authenticated() else None
    most_checked_ = LastDocs.objects.filter(user=user).select_related().order_by('-count')[0:5]
    if not bool_settings(settings.PUBLIC_INDEX) and user is None:
        most_checked_ = []
    return {'updoc_most_checked': most_checked_}
