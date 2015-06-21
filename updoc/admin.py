# -*- coding: utf-8 -*-
from allauth.account.models import EmailAddress, EmailConfirmation
from allauth.socialaccount.models import SocialToken, SocialAccount, SocialApp
from django.contrib.auth import get_user_model
from django.contrib.sites.models import Site
from updoc.models import ProxyfiedHost, RssRoot, RssItem, RewrittenUrl

__author__ = 'flanker'

from django.contrib.admin import site, ModelAdmin, TabularInline
from django.contrib.auth.models import Group


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
site.unregister(SocialToken)
site.unregister(SocialAccount)
site.unregister(SocialApp)
site.unregister(EmailAddress)
site.unregister(EmailConfirmation)
site.register(get_user_model(), UserAdmin)
site.register(RssRoot, RssAdmin)
site.register(RewrittenUrl)
site.register(ProxyfiedHost)
