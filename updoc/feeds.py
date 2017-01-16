# -*- coding: utf-8 -*-
from django.conf import settings
from django.contrib.syndication.views import Feed
from django.core.urlresolvers import reverse
from django.db.models import Q
from django.shortcuts import get_object_or_404
from django.utils.translation import ugettext_lazy as _
from updoc.models import RssItem, UploadDoc, LastDocs, Keyword
from updoc.models import RssRoot

__author__ = 'Matthieu Gallet'


class KeywordFeed(Feed):

    # noinspection PyMethodOverriding
    def get_object(self, request, kw):
        return get_object_or_404(Keyword, value=kw)

    # noinspection PyMethodMayBeStatic
    def title(self, obj):
        return obj.value

    # noinspection PyMethodMayBeStatic
    def link(self, obj):
        return reverse('index') + '?search=' + obj.value

    # noinspection PyMethodMayBeStatic
    def description(self, obj):
        return _("Documentations with keyword %(kw)s") % {'kw': obj.value}

    # noinspection PyMethodMayBeStatic
    def items(self, obj):
        pattern = obj.value
        if len(pattern) > 3:
            docs = UploadDoc.objects.filter(Q(name__icontains=pattern) | Q(keywords__value__icontains=pattern))
        else:
            docs = UploadDoc.objects.filter(Q(name__iexact=pattern) | Q(keywords__value__iexact=pattern))
        return docs.order_by('name')

    def item_title(self, item):
        return item.name

    def item_description(self, item):
        return ''

    def item_link(self, item):
        return item.get_absolute_url(item.index)


class MostViewedDocsFeed(Feed):

    # noinspection PyMethodOverriding
    def get_object(self, request):
        user = request.user
        """:type user: django.contrib.auth.models.User"""
        if user.is_authenticated():
            return request.user
        return None

    # noinspection PyMethodMayBeStatic
    def title(self, obj):
        """:type obj: django.contrib.auth.models.User"""
        if obj is None:
            return _('Favorite documentations')
        return _('Documentations of %(n)s') % {'n': obj.username}

    # noinspection PyMethodMayBeStatic,PyUnusedLocal
    def link(self, obj):
        """:type obj: django.contrib.auth.models.User"""
        return reverse('updoc:my_docs')

    # noinspection PyMethodMayBeStatic,PyUnusedLocal
    def description(self, obj):
        """:type obj: django.contrib.auth.models.User"""
        return _("Most viewed documentations")

    # noinspection PyMethodMayBeStatic
    def items(self, obj):
        """:type obj: django.contrib.auth.models.User"""
        if obj is not None:
            return LastDocs.objects.filter(user=obj).select_related().order_by('-count')[0:30]
        elif not settings.PUBLIC_INDEX or not settings.PUBLIC_DOCS:
            return []
        return LastDocs.objects.filter(user=None).select_related().order_by('-count')[0:30]

    def item_title(self, item):
        """:type item: updoc.models.LastDocs"""
        return item.doc.name

    def item_description(self, item):
        """:type item: updoc.models.LastDocs"""
        return ''

    def item_link(self, item):
        """:type item: updoc.models.LastDocs"""
        return item.doc.get_absolute_url(item.doc.index)


class LastDocsFeed(Feed):

    # noinspection PyMethodOverriding
    def get_object(self, request):
        user = request.user
        """:type user: django.contrib.auth.models.User"""
        if user.is_authenticated():
            return request.user
        return None

    # noinspection PyMethodMayBeStatic,PyUnusedLocal
    def title(self, obj):
        """:type obj: django.contrib.auth.models.User"""
        return _('Last documentations')

    # noinspection PyMethodMayBeStatic,PyUnusedLocal
    def link(self, obj):
        """:type obj: django.contrib.auth.models.User"""
        if obj is not None:
            return reverse('updoc:my_docs')
        return reverse('index')

    # noinspection PyMethodMayBeStatic,PyUnusedLocal
    def description(self, obj):
        """:type obj: django.contrib.auth.models.User"""
        return _("Most recent documentations")

    # noinspection PyMethodMayBeStatic
    def items(self, obj):
        """:type obj: django.contrib.auth.models.User"""
        if obj is None and (not settings.PUBLIC_INDEX or not settings.PUBLIC_DOCS):
            return []
        return UploadDoc.objects.order_by('-upload_time')[0:30]

    def item_title(self, item):
        """:type item: updoc.models.LastDocs"""
        return item.name

    def item_description(self, item):
        """:type item: updoc.models.LastDocs"""
        return ''

    def item_link(self, item):
        """:type item: updoc.models.LastDocs"""
        return item.get_absolute_url(item.index)


class FavoritesFeed(Feed):

    # noinspection PyMethodOverriding
    def get_object(self, request, root_id):
        return get_object_or_404(RssRoot, pk=root_id)

    # noinspection PyMethodMayBeStatic
    def title(self, obj):
        return obj.name

    # noinspection PyMethodMayBeStatic
    def link(self, obj):
        return obj.get_absolute_url()

    # noinspection PyUnusedLocal,PyMethodMayBeStatic
    def description(self, obj):
        return _("List of bookmarks URLs.")

    # noinspection PyMethodMayBeStatic
    def items(self, obj):
        return RssItem.objects.filter(root=obj).order_by('name')

    def item_title(self, item):
        return item.name

    def item_description(self, item):
        return ''

    def item_link(self, item):
        return item.url
