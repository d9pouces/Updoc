# -*- coding: utf-8 -*-
from django.conf import settings
from django.contrib.admin import site, ModelAdmin, TabularInline
from django.contrib.auth import get_user_model
from django.contrib.auth.models import Group
from django.contrib.sites.models import Site
from django.urls import reverse

from updoc.models import ProxyfiedHost, RssRoot, RssItem, RewrittenUrl

__author__ = 'Matthieu Gallet'


class UserAdmin(ModelAdmin):
    fields = ('username', 'first_name', 'last_name', 'email',
              ('is_staff', 'is_superuser'))


class ItemInline(TabularInline):
    model = RssItem


class RssAdmin(ModelAdmin):
    inlines = [ItemInline, ]


site.unregister(get_user_model())
site.unregister(Group)
site.unregister(Site)
# site.unregister(SocialToken)
# site.unregister(SocialAccount)
# site.unregister(SocialApp)
# site.unregister(EmailAddress)
# site.unregister(EmailConfirmation)
site.register(get_user_model(), UserAdmin)
site.register(RssRoot, RssAdmin)
site.register(RewrittenUrl)
site.register(ProxyfiedHost)
site.site_header = settings.DF_PROJECT_NAME
site.site_url = reverse('index')
