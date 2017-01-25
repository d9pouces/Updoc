# -*- coding: utf-8 -*-
import datetime
import locale
import os

from django.core.urlresolvers import reverse
from django.utils.translation import ugettext_lazy as _

from updoc.extensions import EXTENSIONS
__author__ = 'Matthieu Gallet'


class Element(object):
    def __init__(self, icon=None, name=None, url=None, size=None, date=None):
        self.icon = icon
        self.name = name
        self.url = url
        self.size = size
        self.date = date


_directory_icons = {
    'Documents': 'folder-documents',
    _('Documents'): 'folder-documents',
    'Downloads': 'folder-download',
    _('Downloads'): 'folder-download',
    'Library': 'folder-templates',
    _('Library'): 'folder-templates',
    'Movies': 'foler-videos',
    _('Movies'): 'foler-videos',
    'Music': 'folder-music',
    _('Music'): 'folder-music',
    'Pictures': 'folder-pictures',
    _('Pictures'): 'folder-pictures',
    'Public': 'folder-publicshare',
    _('Public'): 'folder-publicshare',
    'System': 'folder-system',
    _('System'): 'folder-system',
    '~': 'user-home',
    'home': 'user-home',
    '.Trash': 'user-trash',
    '.trash': 'user-trash',
}


def get_file_icon(ext, name=None, mimetype=None, is_dir=False, size=32):
    ext_ = ext[1:].lower()
    if name == '..':
        return 'ext-{0}/folder-open.png'.format(size)
    elif is_dir:
        icon = _directory_icons.get(name, 'folder')
        return 'ext-{0}/{1}.png'.format(size, icon)
    elif ext_ in EXTENSIONS:
        return 'ext-{0}/{1}.png'.format(size, EXTENSIONS[ext_])
    elif mimetype is not None:
        s = mimetype.split('/')
        if s[0] == 'image':
            return 'ext-{0}/image-x-generic.png'.format(size)
        elif s[0] == 'audio':
            return 'ext-{0}/audio-x-generic.png'.format(size)
        elif s[0] == 'text':
            return 'ext-{0}/text-plain.png'.format(size)
        else:
            return 'ext-{0}/empty.png'.format(size)
    else:
        return 'ext-{0}/empty.png'.format(size)


def get_icon(name, size=32):
    return 'default_icons/{0}.iconset/icon_{1}x{1}.png'.format(name, size)


class Directory(object):
    def __init__(self, path):
        self.path = path
        self.titles = [(None, x, get_file_icon('', x, is_dir=True, size=16)) for x in path.split('/')]
        self.elements = []

    def set_title_urls(self, dir_view_name=None, dir_view_arg=None, dir_view_kwargs=None):
        dir_view_kwargs[dir_view_arg] = ''
        self.titles = [
            (reverse(dir_view_name, kwargs=dir_view_kwargs), _('root'), get_file_icon('', '~', is_dir=True, size=16))]
        c = ''
        for x in self.path.split('/'):
            c = os.path.join(c, x)
            dir_view_kwargs[dir_view_arg] = c
            if c:
                self.titles.append(
                    (reverse(dir_view_name, kwargs=dir_view_kwargs), x, get_file_icon('', x, is_dir=True, size=16)))

    def append(self, element):
        self.elements.append(element)


def list_directory(root, path, view_name, view_arg='path', view_kwargs=None,
                   dir_view_name=None, dir_view_arg=None, dir_view_kwargs=None,
                   show_files=True, show_dirs=True, show_parent=True, show_hidden=False):
    if view_kwargs is None:
        view_kwargs = {}
    if dir_view_name is None:
        dir_view_name = view_name
    if dir_view_arg is None:
        dir_view_arg = view_arg
    if dir_view_kwargs is None:
        dir_view_kwargs = view_kwargs
    root = os.path.abspath(root)
    dir_path = os.path.abspath(os.path.join(root, path))
    directory = Directory(path)
    if show_dirs:
        directory.set_title_urls(dir_view_name, dir_view_arg, dir_view_kwargs)
    path_len = len(root)
    if root[-1:] == '/':
        path_len -= 1
    if os.path.isdir(dir_path):
        if show_parent:
            full_path = os.path.abspath(os.path.join(dir_path, '..'))
            icon = get_file_icon('', '..', is_dir=True, size=32)
            dir_view_kwargs[dir_view_arg] = full_path[path_len + 1:]
            date = datetime.datetime.fromtimestamp(os.path.getmtime(full_path))
            directory.append(Element(icon, '..', reverse(dir_view_name, kwargs=dir_view_kwargs), None, date))
        listdir = os.listdir(dir_path)
        listdir.sort(key=lambda x: locale.strxfrm(x.lower()))
        for name in listdir:
            if not show_hidden and name and name[0] == '.':
                continue
            full_path = os.path.abspath(os.path.join(dir_path, name))
            truncated_path = full_path[path_len + 1:]
            basename, ext = os.path.splitext(name)
            isdir = os.path.isdir(full_path)
            if isdir or os.path.isfile(full_path):
                icon = get_file_icon(ext, basename, is_dir=isdir, size=32)
                if isdir:
                    dir_view_kwargs[dir_view_arg] = truncated_path
                    url = reverse(dir_view_name, kwargs=dir_view_kwargs)
                    size = None
                else:
                    view_kwargs[view_arg] = truncated_path
                    url = reverse(view_name, kwargs=view_kwargs)
                    size = os.path.getsize(full_path)
                date = datetime.datetime.fromtimestamp(os.path.getmtime(full_path))
                if (show_dirs and isdir) or (show_files and not isdir):
                    directory.append(Element(icon, name, url, size, date))
    return directory


def strip_split(value):
    """Split the value on "," and strip spaces of the result.

    >>> strip_split('keyword1, keyword2 ,,keyword3')
    ["keyword1", "keyword2", "keyword3"]

    :param value:
    :type value:
    :return:
    :rtype:
    """
    if value is None:
        return []
    return [x.strip() for x in value.split(',') if x.strip()]


if __name__ == '__main__':
    import doctest

    doctest.testmod()
