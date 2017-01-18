# coding=utf-8
from urllib import parse

from django.utils.safestring import mark_safe
from django.utils.translation import ugettext as _
from django import template
from django.template.defaultfilters import floatformat

register = template.Library()


@register.filter
def si_unit(value, unit=''):
    if value is None:
        return ''
    sign = ''
    if value < 0:
        sign = '-'
        value = -value
    prefix = ''
    if 1. > value > 0.:
        for prefix in ('', 'm', 'µ', 'n', 'p', 'f', 'a', 'z'):
            if value > 1.:
                break
            value *= 1000.
    else:
        for prefix in ('', 'k', 'M', 'G', 'T', 'P', 'E', 'Z'):
            if value < 1000.:
                break
            value /= 1000.
    return '%s%s %s%s' % (sign, floatformat(value, -2), prefix, _(unit))


@register.filter()
def quote_feed(value):
    return mark_safe(parse.quote_plus(value))
