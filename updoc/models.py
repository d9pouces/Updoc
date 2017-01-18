# -*- coding: utf-8 -*-

# noinspection PyPackageRequirements
import ipaddress
import os
import plistlib
import shutil
from heapq import heappop, heappush

from django.conf import settings
from django.core.urlresolvers import reverse
from django.db import models
from django.db.models.signals import post_delete
from django.dispatch import receiver
from django.http import HttpRequest
from django.utils.functional import cached_property
from django.utils.translation import ugettext_lazy as _
from djangofloor.wsgi.window_info import WindowInfo

from updoc.indexation import delete_archive

__author__ = 'Matthieu Gallet'


def query(cls, request):
    if isinstance(request, HttpRequest):
        if request.user.is_anonymous():
            return cls.objects.filter(user=None)
        return cls.objects.filter(user=request.user)
    assert isinstance(request, WindowInfo)
    if request.user_pk:
        return cls.objects.filter(user__id=request.user_pk)
    return cls.objects.filter(user=None)


class ObjectCache(object):

    def __init__(self, cache_miss_fn, limit=1000):
        self.obj_key = {}
        self.key_list = []
        self.limit = limit
        self.cache_miss_fn = cache_miss_fn

    def get(self, key):
        if key in self.obj_key:
            return self.obj_key[key]
        obj = self.cache_miss_fn(key)
        self.obj_key[key] = obj
        heappush(self.key_list, key)
        if len(self.key_list) > self.limit:
            key = heappop(self.key_list)
            del self.obj_key[key]
        return obj


class Keyword(models.Model):
    value = models.CharField(_('keyword'), max_length=255, db_index=True)
    __cache = None

    def __str__(self):
        return self.value

    @classmethod
    def get(cls, name):
        if cls.__cache is None:
            cls.__cache = ObjectCache(lambda key: cls.objects.get_or_create(value=key)[0])
        return cls.__cache.get(name)


class UploadDoc(models.Model):
    uid = models.CharField(_('uid'), max_length=50, db_index=True)
    name = models.CharField(_('title'), max_length=255, db_index=True, default='')
    path = models.CharField(_('path'), max_length=255, db_index=True)
    keywords = models.ManyToManyField(Keyword, db_index=True, blank=True)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, db_index=True, null=True, blank=True)
    upload_time = models.DateTimeField(_('upload time'), db_index=True, auto_now_add=True)
    version = models.IntegerField(_('version'), default=0, blank=True)

    def __str__(self):
        return self.name

    class Meta:
        """Meta informations on this model"""
        verbose_name = _('documentation')
        verbose_name_plural = _('documentations')

    def get_absolute_url(self, path=''):
        return settings.SERVER_BASE_URL[:-1] + reverse('updoc:show_doc', kwargs={'doc_id': self.id, 'path': path})

    @property
    def uncompressed_root(self):
        return os.path.join(settings.MEDIA_ROOT, 'docs', self.uid[0:2], self.uid)

    @property
    def docset_path(self):
        return os.path.join(settings.MEDIA_ROOT, 'docsets', self.uid[0:2], self.uid + '.tgz')

    @property
    def docset_url(self):
        return settings.SERVER_BASE_URL[:-1] + reverse('updoc:docset', kwargs={'doc_id': self.id})

    @property
    def docset_feed(self):
        return settings.SERVER_BASE_URL[:-1] + reverse('updoc:docset_feed',
                                                       kwargs={'doc_id': self.id, 'doc_name': self.name})

    @property
    def zip_path(self):
        return os.path.join(settings.MEDIA_ROOT, 'zip', self.uid[0:2], self.uid + '.zip')

    @cached_property
    def index(self):
        path = str(self.path)
        index_path = None
        prefix = ''
        searched_files = ['index.html', 'index.htm', 'index.md', 'README.md']
        if os.path.isfile(path):
            index_path = path
        elif os.path.isdir(path):
            documents_dir = os.path.join(path, 'Contents', 'Resources', 'Documents')
            plist_path = os.path.join(path, 'Contents', 'Info.plist')
            if os.path.isdir(documents_dir) and os.path.isfile(plist_path):
                with open(plist_path, 'rb') as fd:
                    content = plistlib.load(fd)
                prefix = 'Contents/Resources/Documents/'
                if 'dashIndexFilePath' in content:
                    searched_files = [content['dashIndexFilePath']] + searched_files
            index_path = ''
            for index in searched_files:
                if os.path.isfile(os.path.join(path, prefix + index)):
                    index_path = prefix + index
                    break
            else:
                ldir = os.listdir(path)
                if len(ldir) == 1 and os.path.isfile(os.path.join(path, ldir[0])):
                    index_path = ldir[0]
        return index_path

    def clean_archive(self):
        for path in str(self.path), self.docset_path, self.zip_path:
            if os.path.isfile(path):
                os.remove(path)
            elif os.path.exists(path):
                shutil.rmtree(path)
        if self.id:
            delete_archive(self.id)

    def delete(self, using=None, keep_parents=False):
        self.clean_archive()
        self.keywords.clear()
        super(UploadDoc, self).delete(using=using, keep_parents=keep_parents)

    @classmethod
    def query(cls, request):
        # noinspection PyTypeChecker
        return query(cls, request)


# noinspection PyUnusedLocal
@receiver(post_delete, sender=UploadDoc)
def my_handler(sender, instance=None, **kwargs):
    instance.clean_archive()


class LastDocs(models.Model):
    doc = models.ForeignKey(UploadDoc, db_index=True)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, db_index=True, null=True, blank=True)
    count = models.IntegerField(db_index=True, blank=True, default=1)
    last = models.DateTimeField(_('last'), db_index=True, auto_now=True)

    @classmethod
    def query(cls, request):
        # noinspection PyTypeChecker
        return query(cls, request)


class RewrittenUrl(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, db_index=True, null=True, blank=True)
    src = models.CharField(_('Original URL'), db_index=True, max_length=255)
    dst = models.CharField(_('New URL'), db_index=True, max_length=255, blank=True, default='')

    class Meta:
        verbose_name = _('Rewritten URL')
        verbose_name_plural = _('Rewritten URLs')

    def __str__(self):
        return '%s -> %s' % (self.src, self.dst)

    @classmethod
    def query(cls, request):
        # noinspection PyTypeChecker
        return query(cls, request)


class ProxyfiedHost(models.Model):
    host = models.CharField(_('URL to proxify'), db_index=True, max_length=255, blank=True, default='',
                            help_text='Can be a regexp on URL (like http://*.example.com:*/*) or a '
                                      'subnet (like 192.168.0.0/24). Leave it blank to use as default value.')
    proxy = models.CharField(_('Proxy to use'), db_index=True, max_length=255, blank=True, default='',
                             help_text=_('e.g. proxy.example.com:8080. Leave it empty if direct connexion. '
                                         'Several values can be given, separated by semi-colons (;).'))
    priority = models.IntegerField(_('Priority'), db_index=True, default=0, blank=True,
                                   help_text=_('Low priorities are written first in proxy.pac'))

    class Meta:
        verbose_name = _('Proxyfied host')
        verbose_name_plural = _('Proxified hosts')

    def __str__(self):
        return _('%(h)s via %(p)s') % {'h': self.host, 'p': self.proxy}

    def network(self):
        try:
            return ipaddress.ip_network(self.host)
        except ValueError:
            return None

    @staticmethod
    def name_to_proxy(x):
        x = x.strip()
        if not x:
            return 'DIRECT'
        return 'PROXY %s' % x

    def proxy_str(self):
        return '; '.join([self.name_to_proxy(x) for x in self.proxy.split(';')])


class RssRoot(models.Model):
    name = models.CharField(_('name'), db_index=True, max_length=255)

    @staticmethod
    def get_absolute_url():
        return settings.SERVER_BASE_URL[:-1] + reverse('index')

    class Meta:
        verbose_name = _('favorite group')
        verbose_name_plural = _('favorite groups')

    def __str__(self):
        return self.name


class RssItem(models.Model):
    root = models.ForeignKey(RssRoot, verbose_name=_('root'), db_index=True)
    name = models.CharField(_('name'), db_index=True, max_length=255)
    url = models.URLField(_('URL'), db_index=True, max_length=255)

    class Meta:
        verbose_name = _('element')
        verbose_name_plural = _('elements')

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        return self.url
