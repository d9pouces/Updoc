# -*- coding: utf-8 -*-
import mimetypes
import os
import re
import stat
import tarfile
import tempfile
import datetime
import zipfile

from django.conf import settings
from django.contrib import messages
from django.contrib.auth.decorators import login_required, permission_required
from django.core.exceptions import PermissionDenied
from django.core.files.uploadedfile import UploadedFile
from django.core.urlresolvers import reverse
from django.db.models import F
from django.http.response import HttpResponseRedirect, Http404, HttpResponse, StreamingHttpResponse, HttpResponseNotModified
from django.utils.safestring import mark_safe
from django.utils.text import slugify
from django.utils.timezone import utc
from django.utils.translation import ugettext_lazy as _
from django.shortcuts import render_to_response, get_object_or_404
from django.template import RequestContext
from django.views.decorators.cache import cache_control, cache_page
from django.views.decorators.csrf import csrf_exempt
from django.views.static import was_modified_since
import markdown

from djangofloor.views import send_file
from updoc.forms import UrlRewriteForm, FileUploadForm, UploadApiForm, MetadatadUploadForm
from updoc.models import ProxyfiedHost, RssRoot, RssItem, RewrittenUrl, UploadDoc, Keyword, LastDocs
from updoc.process import process_new_file
from updoc.utils import bool_settings, strip_split, list_directory

__author__ = 'flanker'


range_re = re.compile(r'bytes=(\d+)-(\d+)')
replace_cache = {'until': None, 're': None, 'validity': datetime.timedelta(0, 600), 'rep_dict': None, }


def send_file_replace_url(request, filename, allow_replace=False):
    """
    :param request:
    :type request:
    :param filename:
    :type filename:
    :param allow_replace:
    :type allow_replace:
    :return:
    :rtype:
    """
    # Respect the If-Modified-Since header.
    if not os.path.isfile(filename):
        raise Http404
    statobj = os.stat(filename)
    if not was_modified_since(request.META.get('HTTP_IF_MODIFIED_SINCE'), statobj[stat.ST_MTIME], statobj[stat.ST_SIZE]):
        return HttpResponseNotModified()
    content_type = mimetypes.guess_type(filename)[0]
    extension = filename.rpartition('.')[2]
    if allow_replace and extension in {'js', 'html', 'css', 'md', 'txt', } and os.path.getsize(filename) < 100 * 1024:
        now = datetime.datetime.now()
        if replace_cache['re'] is None or replace_cache['until'] < now:
            replace_cache['until'] = now + replace_cache['validity']
            rep_dict = dict([(x.src, x.dst) for x in RewrittenUrl.objects.all()])
            replace_cache['rep_dict'] = rep_dict
            replace_cache['re'] = re.compile("|".join([re.escape(k) for k in rep_dict.keys()]), re.M)
        if replace_cache['rep_dict']:
            try:
                with open(filename, 'r', encoding='utf-8') as out_fd:
                    content = out_fd.read()
                    content = replace_cache['re'].sub(lambda x: replace_cache['rep_dict'][x.group(0)], content)
                return HttpResponse(content, content_type=content_type)
            except UnicodeDecodeError:
                pass
    return send_file(filename, mimetype=content_type)


def compress_archive(request, doc_id, fmt='zip'):
    if request.user.is_anonymous() and not settings.PUBLIC_DOCS:
        raise Http404
    tmp_file = tempfile.NamedTemporaryFile()
    doc = get_object_or_404(UploadDoc, id=doc_id)
    arc_root = slugify(doc.name)
    if fmt == 'zip':
        compression_file = zipfile.ZipFile(tmp_file, mode='w', compression=zipfile.ZIP_DEFLATED)
        for (root, dirnames, filenames) in os.walk(doc.path):
            for filename in filenames:
                full_path = os.path.join(root, filename)
                arcname = os.path.join(arc_root, os.path.relpath(full_path, doc.path))
                compression_file.write(full_path, arcname)
        content_type = 'application/zip'
    elif fmt in ('gz', 'bz2', 'xz'):
        compression_file = tarfile.open(name=arc_root + '.tar.' + fmt, mode='w:' + fmt, fileobj=tmp_file)
        for filename in os.listdir(doc.path):
            full_path = os.path.join(doc.path, filename)
            arcname = os.path.join(arc_root, os.path.relpath(full_path, doc.path))
            compression_file.add(full_path, arcname)
        content_type = 'application/x-tar'
    else:
        raise ValueError
    compression_file.close()
    tmp_file.seek(0)
    response = StreamingHttpResponse(tmp_file, content_type=content_type)
    response['Content-Disposition'] = 'attachment; filename="%s"' % arc_root
    return response


@cache_control(no_cache=True)
def index(request):
    template_values = {}
    return render_to_response('updoc/index.html', template_values, RequestContext(request))


@cache_control(no_cache=True)
def show_favorite(request, root_id=None):
    if request.user.is_anonymous() and not bool_settings(settings.PUBLIC_BOOKMARKS):
        roots = []
        favorites = []
        messages.info(request, _('You must be logged to see this page.'))
        current_root_name = _('Bookmarks')
        root_id = 0
    else:
        roots = list(RssRoot.objects.all().order_by('name'))
        if root_id is None and roots:
            root_id = roots[0].id
        elif not root_id:
            root_id = 0
        if root_id:
            current_root_name = get_object_or_404(RssRoot, id=root_id).name
        else:
            current_root_name = _('Bookmarks')
        favorites = RssItem.objects.filter(root__id=root_id).order_by('name')
    template_values = {'roots': roots, 'values': favorites, 'current_root_name': current_root_name,
                       'current_id': int(root_id)}
    return render_to_response('updoc/list_favorites.html', template_values, RequestContext(request))


@cache_page(60 * 15)
def show_proxies(request):
    proxies = ProxyfiedHost.objects.exclude(host='').order_by('priority')
    defaults = '; '.join([x.proxy_str() for x in ProxyfiedHost.objects.filter(host='').order_by('priority')])
    if request.user.is_anonymous() and not bool_settings(settings.PUBLIC_PROXIES):
        proxies = []
        defaults = ''
    if not defaults:
        defaults = 'DIRECT'
    template_values = {'proxies': proxies, 'model': ProxyfiedHost, 'defaults': defaults}
    return render_to_response('proxy.pac', template_values, content_type='application/x-ns-proxy-autoconfig')


@cache_control(no_cache=True)
def my_docs(request):
    user = request.user if request.user.is_authenticated() else None
    if request.method == 'POST':
        form = UrlRewriteForm(request.POST)
        if form.is_valid():
            RewrittenUrl(user=user, src=form.cleaned_data['src'], dst=form.cleaned_data['dst']).save()
            messages.info(request, _('URL %(src)s will be rewritten as %(dst)s') % form.cleaned_data)
            return HttpResponseRedirect(reverse('updoc.views.my_docs'))
    else:
        form = UrlRewriteForm()
    uploads = UploadDoc.query(request).order_by('-upload_time').select_related()
    rw_urls = RewrittenUrl.query(request).order_by('src')
    template_values = {'uploads': uploads, 'title': _('My documents'), 'rw_urls': rw_urls,
                       'rw_form': form, 'editable': True}
    return render_to_response('updoc/my_docs.html', template_values, RequestContext(request))


@csrf_exempt
def delete_url(request, url_id):
    if request.method != 'POST':
        return HttpResponseRedirect(reverse('updoc.views.my_docs'))
    url = get_object_or_404(RewrittenUrl.query(request), pk=url_id)
    RewrittenUrl.query(request).filter(pk=url_id).delete()
    messages.info(request, _('The replacement of %(src)s by %(dst)s has been removed') % {'src': url.src, 'dst': url.dst, })
    return HttpResponseRedirect(reverse('updoc.views.my_docs'))


@csrf_exempt
def delete_doc(request, doc_id):
    obj = get_object_or_404(UploadDoc.query(request), id=doc_id)
    name = obj.name
    try:
        obj.delete()
        messages.info(request, _('%(doc)s successfully deleted') % {'doc': name})
    except IOError:
        messages.error(request, _('Unable to delete %(doc)s ') % {'doc': name})
    return HttpResponseRedirect(reverse('updoc.views.my_docs'))


@login_required(login_url='/accounts/login/')
def upload(request):
    """Index view, displaying and processing a form."""
    if request.method == 'POST':
        form = MetadatadUploadForm(request.POST)
        if form.is_valid():
            messages.info(request, _('File successfully uploaded'))
            obj = get_object_or_404(UploadDoc.query(request), id=form.cleaned_data['pk'])
            obj.name = form.cleaned_data['name']
            for keyword in form.cleaned_data['keywords'].lower().split():
                obj.keywords.add(Keyword.get(keyword))
            obj.save()
            return HttpResponseRedirect(reverse('updoc.views.upload'))
        elif 'pk' in form.cleaned_data:
            obj = get_object_or_404(UploadDoc.query(request), id=form.cleaned_data['pk'])
            obj.delete()
            messages.error(request, _('Unable to upload this file'))
        else:
            messages.error(request, _('Unable to upload this file'))
    else:
        form = FileUploadForm()
    template_values = {'form': form, 'title': _('Upload a new file'), 'root_host': settings.HOST}
    return render_to_response('updoc/upload.html', template_values, RequestContext(request))


@csrf_exempt
@permission_required('updoc.add_uploaddoc')
def upload_doc_progress(request):
    form = FileUploadForm(request.POST, request.FILES)
    if not form.is_valid():
        raise PermissionDenied
    uploaded_file = request.FILES['file']
    obj = process_new_file(uploaded_file, request)
    # offer a correct name for the newly uploaded document
    basename = os.path.basename(uploaded_file.name).rpartition('.')[0]
    if basename[-4:] == '.tar':
        basename = basename[:-4]
    form = MetadatadUploadForm(initial={'pk': obj.pk, 'name': basename, })
    template_values = {'form': form, }
    return render_to_response('updoc/upload_doc_progress.html', template_values, RequestContext(request))


@csrf_exempt
def upload_doc_api(request):
    user = request.user if request.user.is_authenticated() else None
    if user is None:
        # username = request.GET.get('username', '')
        # password = request.GET.get('password', '')
        # username = unquote(username)
        # password = unquote(password)
        # if username and password:
        #     users = get_user_model().objects.filter(username=username)[0:1]
        #     if not users:
        #         return HttpResponse(_('Invalid user %(u)s') % {'u': username}, status=401)
        #     user = users[0]
        #     if not user.check_password(password):
        #         return HttpResponse(_('Invalid password for user %(u)s') % {'u': username}, status=401)
        #     request.user = user
        # else:
        return HttpResponse(_('You must be logged to upload files.'), status=401)
    elif request.method != 'POST':
        return HttpResponse(_('Only POST requests are allowed.'), status=400)
    form = UploadApiForm(request.GET)
    if not form.is_valid():
        raise Http404
    # read the request and push it into a tmp file
    tmp_file = tempfile.TemporaryFile(mode='w+b')
    c = False
    chunk = request.read(32768)
    while chunk:
        tmp_file.write(chunk)
        c = True
        chunk = request.read(32768)
    tmp_file.flush()
    tmp_file.seek(0)
    if not c:
        return HttpResponse(_('Empty file. You must POST a valid file.'), status=400)
    # ok, we have the tmp file
    uploaded_file = UploadedFile(name=form.cleaned_data['filename'], file=tmp_file)

    existing_obj = None
    existing_objs = list(UploadDoc.objects.filter(user=user, name=form.cleaned_data['name'])[0:1])
    if existing_objs:
        existing_obj = existing_objs[0]
        existing_obj.clean_archive()
    try:
        obj = process_new_file(uploaded_file, request, obj=existing_obj)
        obj.name = form.cleaned_data['name']
        obj.save()
        for keyword in strip_split(form.cleaned_data['keywords'].lower()):
            obj.keywords.add(Keyword.get(keyword))
    except Exception as e:
        return HttpResponse(str(e), status=400)
    finally:
        tmp_file.close()
    return HttpResponse(_('File successfully uploaded and indexed.'), status=200)


def show_doc_alt(request, doc_id, path=''):
    return show_doc(request, doc_id, path=path)


def show_doc(request, doc_id, path=''):
    if request.user.is_anonymous() and not bool_settings(settings.PUBLIC_DOCS):
        raise Http404
    doc = get_object_or_404(UploadDoc, id=doc_id)
    root_path = doc.path
    full_path = os.path.join(root_path, path)
    if not full_path.startswith(root_path):
        raise Http404
    user = request.user if request.user.is_authenticated() else None
    checked, created = LastDocs.objects.get_or_create(user=user, doc=doc)
    use_auth = reverse('updoc.views.show_doc', kwargs={'doc_id': doc_id, 'path': path}) == request.path
    view = 'updoc.views.show_doc' if use_auth else 'updoc.views.show_doc_alt'
    if not created:
        now = datetime.datetime.utcnow().replace(tzinfo=utc)
        LastDocs.objects.filter(user=user, doc=doc).update(count=F('count') + 1, last=now)
    editable = request.user.is_superuser or request.user == doc.user
    if not os.path.isfile(full_path):
        directory = list_directory(root_path, path, view, view_arg='path',
                                   view_kwargs={'doc_id': doc.id}, dir_view_name=view,
                                   dir_view_arg='path', dir_view_kwargs={'doc_id': doc.id}, show_files=True,
                                   show_dirs=True, show_parent=True, show_hidden=False)
        template_values = {'directory': directory, 'doc': doc, 'editable': editable, 'title': str(doc),
                           'keywords': ' '.join([keyword.value for keyword in doc.keywords.all()]), 'doc_id': doc_id, }
        return render_to_response('updoc/list_dir.html', template_values, RequestContext(request))
    if full_path.endswith('.md'):
        view_name = 'updoc.views.show_doc'
        if request.user.is_anonymous():
            view_name = 'updoc.views.show_doc_alt'
        path_components = [(reverse(view_name, kwargs={'doc_id': doc_id, 'path': ''}), _('root'))]
        components = path.split('/')
        for index_, comp in enumerate(components):
            p = '/'.join(components[0:index_ + 1])
            path_components.append((reverse(view_name, kwargs={'doc_id': doc_id, 'path': p}), comp))
        template_values = {'doc': doc, 'editable': editable, 'title': str(doc), 'path': path, 'paths': path_components,
                           'keywords': ' '.join([keyword.value for keyword in doc.keywords.all()]), 'doc_id': doc_id, }
        try:
            with open(full_path) as fd:
                content = fd.read()
            template_values['content'] = mark_safe(markdown.markdown(content))
            return render_to_response('updoc/markdown.html', template_values, RequestContext(request))
        except UnicodeDecodeError:
            pass
    return send_file_replace_url(request, full_path, allow_replace=True)
