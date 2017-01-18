# coding=utf-8
import os
import tempfile
import uuid
from argparse import ArgumentParser
from urllib.parse import urlparse

import requests
from django.contrib.auth import get_user_model
from django.core.management import BaseCommand

from updoc.models import Keyword, UploadDoc
from updoc.process import process_uploaded_file

__author__ = 'Matthieu Gallet'


class AddPackage(BaseCommand):

    def add_arguments(self, parser):
        assert isinstance(parser, ArgumentParser)
        parser.add_argument('filename', default=None,
                            help='filename or http-URL to add'),
        parser.add_argument('-k', '--keyword', action='append', dest='keyword', default=[],
                            help='Keyword to append to the uploaded archive'),
        parser.add_argument('-n', '--name', action='store', dest='name', default=None,
                            help='Name of the archive. If an archive with the same name already exists, nothing is done'),
        parser.add_argument('-u', '--user', action='store', dest='user', default=None,
                            help='username in behalf the upload is done of.'),

    def handle(self, *args, **options):
        # require
        user = None
        if options['user'] is not None:
            user = get_user_model().objects.get(username=options['user'])

        filename = options['filename']
        if filename.startswith('file://'):
            filename = filename[7:]
        if filename.startswith('http://') or filename.startswith('https://'):
            parsed_url = urlparse(filename)
            basename = os.path.basename(parsed_url.path)
            src_file = tempfile.NamedTemporaryFile()
            req = requests.get(filename, stream=True)
            chunk_size = 16384
            for chunk in req.iter_content(chunk_size):
                src_file.write(chunk)
        else:
            src_file = open(filename, mode='rb')
            basename = os.path.basename(filename)

        obj = UploadDoc(uid=str(uuid.uuid1()), user=user, name=options['name'] or basename)
        obj.save()
        process_uploaded_file(obj, src_file, basename)
        for keyword in options['keyword']:
            obj.keywords.add(Keyword.get(keyword.lower().strip()))
        obj.save()
