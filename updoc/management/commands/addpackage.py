# coding=utf-8
from optparse import make_option
from urllib.parse import urlparse
import requests
import tempfile
from django.contrib.auth import get_user_model
from django.contrib.auth.models import AnonymousUser
from django.core.files.uploadedfile import UploadedFile
from django.core.management import BaseCommand
from django.http.request import HttpRequest
import os
from updoc.process import process_new_file
from updoc.models import Keyword

__author__ = 'flanker'


class AddPackage(BaseCommand):

    option_list = (
        make_option('-k', '--keyword', action='append', dest='keyword', default=[],
                    help='Keyword to append to the uploaded archive'),
        make_option('-n', '--name', action='store', dest='name', default=None,
                    help='Name of the archive. If an archive with the same name already exists, nothing is done'),
        make_option('-u', '--user', action='store', dest='user', default=None,
                    help='username in behalf the upload is done of.'),
    ) + BaseCommand.option_list

    def handle(self, *args, **options):
        if not args:
            print('Please provid either a file or a URL ')
            return 1
        # require
        request = HttpRequest()
        if options['user'] is None:
            request.user = AnonymousUser()
        else:
            request.user = get_user_model().objects.get(username=options['user'])

        filename = args[0]
        if filename.startswith('file://'):
            filename = filename[7:]
        if filename.startswith('http://') or filename.startswith('https://'):
            parsed_url = urlparse(filename)
            basename = os.path.basename(parsed_url.path)
            src_file = tempfile.NamedTemporaryFile()
            req = requests.get(filename, stream=True)
            chunk_size = 16384
            size = 0
            for chunk in req.iter_content(chunk_size):
                src_file.write(chunk)
                size += len(chunk)
        else:
            src_file = open(filename, mode='rb')
            basename = os.path.basename(filename)
            size = os.path.getsize(filename)

        uploaded_file = UploadedFile(file=src_file, name=basename, size=size)
        obj = process_new_file(uploaded_file, request)
        if options['name'] is not None:
            obj.name = options['name']
        for keyword in options['keyword']:
            obj.keywords.add(Keyword.get(keyword.lower().strip()))
        obj.save()
