# -*- coding: utf-8 -*-
from django import forms
from django.utils.translation import ugettext_lazy as _

__author__ = 'Matthieu Gallet'


class FileUploadForm(forms.Form):
    """Upload form"""
    file = forms.FileField(label=_('file'), max_length=255)


class DocSearchForm(forms.Form):
    """Upload form"""
    search = forms.CharField(max_length=255)
    doc_id = forms.IntegerField(widget=forms.widgets.HiddenInput(), required=False)


class MetadatadUploadForm(forms.Form):
    """Upload form"""
    pk = forms.IntegerField(widget=forms.widgets.HiddenInput())
    name = forms.CharField(label=_('Name'), max_length=240,
                           widget=forms.widgets.TextInput(attrs={'placeholder': _('Please enter a name'), }))
    keywords = forms.CharField(label=_('Keywords'), max_length=255, required=False,
                               widget=forms.widgets.TextInput(attrs={'placeholder': _('Please enter some keywords'), }))


class UploadApiForm(forms.Form):
    filename = forms.CharField(label=_('Filename'), max_length=240)
    name = forms.CharField(label=_('Name'), max_length=240)
    keywords = forms.CharField(label=_('Keywords'), max_length=255, required=False)


class UrlRewriteForm(forms.Form):
    """form for new URL to rewrite"""
    src = forms.URLField(label=_('URL to rewrite'), max_length=255)
    dst = forms.URLField(label=_('New URL'), max_length=255)
