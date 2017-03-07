# -*- coding: utf-8 -*-
import re

__author__ = 'Matthieu Gallet'


def avatar(request, hashed):
    size_str = request.GET.get('s', '64')
    if re.match('^\d+$', size_str):
        size = max(1, min(200, int(size_str)))
    else:
        size = 80
    default = request.GET.get('d')
    default_values = {'404', 'mm', 'identicon', 'monsterid', 'wavatar', 'retro', 'blank'}
    force_default = request.GET.get('f') == 'y' or request.GET.get('forcedefault') == 'y'


def profile(request, hashed):
    pass


def json(request, hashed):
    pass


def xml(request, hashed):
    pass


def vcard(request, hashed):
    pass


def qr_code(request, hashed):
    pass
