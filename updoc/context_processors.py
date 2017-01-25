# -*- coding: utf-8 -*-
from django.conf import settings

from updoc import __version__
from updoc.models import LastDocs, ProxyfiedHost, RssRoot

__author__ = 'Matthieu Gallet'


def most_checked(request):
    user = request.user if request.user.is_authenticated() else None
    most_checked_ = LastDocs.query(request).select_related('doc').order_by('-count')[0:5]
    if not settings.PUBLIC_INDEX and user is None:
        most_checked_ = []
    has_proxyfied_hosts = ProxyfiedHost.objects.all().count() > 0
    has_rss_hosts = RssRoot.objects.all().count() > 0
    return {'updoc_most_checked': most_checked_, 'updoc_version': __version__,
            'has_proxyfied_hosts': has_proxyfied_hosts, 'has_rss_hosts': has_rss_hosts}
