# -*- coding: utf-8 -*-
"""Generate Dash docset
====================
https://kapeli.com/docsets#dashDocset

"""
import os
import plistlib
import re

import sqlite3
import tarfile
import tempfile

import shutil

from django.conf import settings
from django.utils.text import slugify
from djangofloor.utils import ensure_dir


__author__ = 'Matthieu Gallet'


class Docset(object):
    def __init__(self, doc):
        from updoc.models import UploadDoc
        self.doc = doc
        assert isinstance(self.doc, UploadDoc)

    def prepare(self):
        path = self.doc.path
        documents_dir = os.path.join(path, 'Contents', 'Resources', 'Documents')
        plist_path = os.path.join(path, 'Contents', 'Info.plist')
        if os.path.isdir(documents_dir) and os.path.isfile(plist_path):
            with tempfile.TemporaryDirectory(dir=settings.FILE_UPLOAD_TEMP_DIR) as dirname:
                root = os.path.join(dirname, '%s.docset' % slugify(self.doc.name))
                shutil.copytree(self.doc.path, root)
                self.write_docset(dirname)
            return
        with tempfile.TemporaryDirectory(dir=settings.FILE_UPLOAD_TEMP_DIR) as dirname:
            root = os.path.join(dirname, '%s.docset' % slugify(self.doc.name), 'Contents')
            ensure_dir(os.path.join(root, 'Resources'), parent=False)
            index_path = self.doc.index
            with open(os.path.join(root, 'Info.plist'), 'wb') as fd:
                info = {'CFBundleIdentifier': slugify(self.doc.name), 'CFBundleName': self.doc.name,
                        'DocSetPlatformFamily': slugify(self.doc.name), 'isDashDocset': True,
                        'isJavaScriptEnabled': True}
                if index_path:
                    info['dashIndexFilePath'] = index_path
                plistlib.dump(info, fd)
            shutil.copytree(self.doc.uncompressed_root, os.path.join(root, 'Resources', 'Documents'))
            self.create_index(root)
            self.write_docset(dirname)

    def write_docset(self, dirname):
        ensure_dir(self.doc.docset_path)
        with open(self.doc.docset_path, 'wb') as tmp_file:
            arc_root = slugify(self.doc.name)
            compression_file = tarfile.open(name=arc_root + '.gz', mode='w:gz', fileobj=tmp_file)
            for filename in os.listdir(dirname):
                full_path = os.path.join(dirname, filename)
                arcname = os.path.join(os.path.relpath(full_path, dirname))
                compression_file.add(full_path, arcname)
            compression_file.close()

    def create_index(self, root):
        index_filename = os.path.join(root, 'Resources', 'docSet.dsidx')
        conn = sqlite3.connect(index_filename)
        cur = conn.cursor()
        # cur.execute('DROP TABLE searchIndex;')
        cur.execute('CREATE TABLE searchIndex(id INTEGER PRIMARY KEY, name TEXT, type TEXT, path TEXT);')
        cur.execute('CREATE UNIQUE INDEX anchor ON searchIndex (name, type, path);')
        src_path = self.doc.uncompressed_root
        for root, dirnames, filenames in os.walk(src_path):
            for filename in filenames:
                ext = filename.rpartition('.')[2]
                if ext not in ('html', 'htm'):
                    continue
                full_path = os.path.join(root, filename)
                with open(full_path, 'r', encoding='utf-8') as fd:
                    for line in fd:
                        matcher = re.match('^.*<h[1-2]>(.*)</h[1-2]>.*$', line)
                        if not matcher:
                            continue
                        path = os.path.relpath(full_path, src_path)
                        cur.execute('INSERT OR IGNORE INTO searchIndex(name, type, path) VALUES (?,?,?)',
                                    (matcher.group(1), 'func', path))
        conn.commit()
        conn.close()

