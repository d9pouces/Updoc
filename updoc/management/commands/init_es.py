# coding=utf-8
from django.conf import settings
from django.contrib.auth.models import Group
from django.contrib.auth.models import Permission
from django.core.management import BaseCommand

from updoc.indexation import create_index, index_archive
from updoc.models import UploadDoc
from updoc.progress.progressbar import ProgressBar
from updoc.progress.widgets import Bar, Percentage

__author__ = 'flanker'


class ImportProgressBar(ProgressBar):
    def __init__(self, model):
        print('Indexing %s...' % model.__name__)
        super(ImportProgressBar, self).__init__(widgets_=[Percentage(), Bar()], maxval=model.objects.count())
        self.__pb_value = 0
        self.start()

    def add(self):
        self.__pb_value += 1
        if self.__pb_value >= self.maxval or self.__pb_value % 10 == 0:
            super(ImportProgressBar, self).update(self.__pb_value)


class Command(BaseCommand):
    """Print basic configuration files for different kinds of deployment"""
    args = ''
    help = 'Initialize ElasticSearch index'

    def handle(self, *args, **options):
        queries = create_index()
        for query in queries:
            if query and query.status_code > 400:
                print(query.status_code, query.text)
            else:
                print('ok')
        # noinspection PyTypeChecker
        pb = ImportProgressBar(UploadDoc)
        for updoc in UploadDoc.objects.all():
            index_archive(updoc.id, updoc.path)
            pb.add()
        pb.finish()
        a = Group.objects.get_or_create(name=str(settings.FLOOR_DEFAULT_GROUP_NAME))[0]
        p = Permission.objects.get(codename='add_uploaddoc')
        a.permissions.add(p)
