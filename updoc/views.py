# -*- coding: utf-8 -*-
import datetime
import mimetypes
import os
import re
import stat
import tarfile
import tempfile
import uuid
import zipfile

import markdown
from django.conf import settings
from django.contrib import messages
from django.contrib.auth.decorators import login_required, permission_required
from django.core.exceptions import PermissionDenied
from django.core.urlresolvers import reverse
from django.db.models import F, Count, Q
from django.http.response import HttpResponseRedirect, Http404, HttpResponse, StreamingHttpResponse,\
    HttpResponseNotModified
from django.shortcuts import get_object_or_404
from django.template.response import TemplateResponse
from django.utils.safestring import mark_safe
from django.utils.text import slugify
from django.utils.timezone import utc
from django.utils.translation import ugettext_lazy as _
from django.views.decorators.cache import cache_page, never_cache
from django.views.decorators.csrf import csrf_exempt
from django.views.static import was_modified_since
from elasticsearch.exceptions import ConnectionError as ESError

from djangofloor.tasks import scall, SERVER, set_websocket_topics
from djangofloor.views import send_file
from updoc.forms import UrlRewriteForm, FileUploadForm, UploadApiForm, MetadatadUploadForm, DocSearchForm
from updoc.indexation import search_archive
from updoc.models import ProxyfiedHost, RssRoot, RssItem, RewrittenUrl, UploadDoc, Keyword, LastDocs
from updoc.utils import strip_split, list_directory

__author__ = 'Matthieu Gallet'


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
    if not was_modified_since(request.META.get('HTTP_IF_MODIFIED_SINCE'),
                              statobj[stat.ST_MTIME], statobj[stat.ST_SIZE]):
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

    doc = get_object_or_404(UploadDoc, id=doc_id)
    assert isinstance(doc, UploadDoc)
    arc_root = slugify(doc.name)
    compression_file = None
    if fmt == 'zip':
        if os.path.isfile(doc.zip_path):
            tmp_file = open(doc.zip_path, 'rb')
        else:
            tmp_file = tempfile.NamedTemporaryFile(dir=settings.FILE_UPLOAD_TEMP_DIR)
            compression_file = zipfile.ZipFile(tmp_file, mode='w', compression=zipfile.ZIP_DEFLATED)
            for (root, dirnames, filenames) in os.walk(doc.path):
                for filename in filenames:
                    full_path = os.path.join(root, filename)
                    arcname = os.path.join(arc_root, os.path.relpath(full_path, doc.path))
                    compression_file.write(full_path, arcname)
        content_type = 'application/zip'
    elif fmt in ('gz', 'bz2', 'xz'):
        tmp_file = tempfile.NamedTemporaryFile(dir=settings.FILE_UPLOAD_TEMP_DIR)
        compression_file = tarfile.open(name=arc_root + '.tar.' + fmt, mode='w:' + fmt, fileobj=tmp_file)
        for filename in os.listdir(doc.path):
            full_path = os.path.join(doc.path, filename)
            arcname = os.path.join(arc_root, os.path.relpath(full_path, doc.path))
            compression_file.add(full_path, arcname)
        content_type = 'application/x-tar'
    else:
        raise ValueError
    if compression_file:
        compression_file.close()
    tmp_file.seek(0)
    response = StreamingHttpResponse(tmp_file, content_type=content_type)
    response['Content-Disposition'] = 'attachment; filename="%s"' % arc_root
    return response


@never_cache
def index(request):
    if request.user.is_authenticated():
        set_websocket_topics(request)
    if request.user.is_anonymous() and not settings.PUBLIC_INDEX:
        messages.info(request, _('You must be logged to see documentations.'))
        keywords_with_counts, recent_uploads, recent_checked = [], [], []
    else:
        keywords_with_counts = Keyword.objects.all().annotate(count=Count('uploaddoc')).filter(count__gt=0)\
            .order_by('-count')[0:15]
        recent_uploads = UploadDoc.objects.order_by('-upload_time')[0:10]
        recent_checked = LastDocs.query(request).select_related().order_by('-last')[0:20]
    if request.user.is_anonymous() and not settings.PUBLIC_BOOKMARKS:
        rss_roots = []
    else:
        rss_roots = RssRoot.objects.all().order_by('name')
    template_values = {'recent_checked': recent_checked, 'title': _('Updoc'), 'rss_roots': rss_roots,
                       'recent_uploads': recent_uploads, 'keywords': keywords_with_counts,
                       'show_all_link': True, 'list_title': _('Recent uploads'), }
    return TemplateResponse(request, 'updoc/index.html', template_values)


@never_cache
def show_favorite(request, root_id=None):
    if request.user.is_authenticated():
        set_websocket_topics(request)
    if request.user.is_anonymous() and not settings.PUBLIC_BOOKMARKS:
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
    return TemplateResponse(request, 'updoc/list_favorites.html', template_values)


@cache_page(60 * 15)
def show_proxies(request):
    proxies = ProxyfiedHost.objects.exclude(host='').order_by('priority')
    defaults = '; '.join([x.proxy_str() for x in ProxyfiedHost.objects.filter(host='').order_by('priority')])
    if request.user.is_anonymous() and not settings.PUBLIC_PROXIES:
        proxies = []
        defaults = ''
    if not defaults:
        defaults = 'DIRECT'
    template_values = {'proxies': proxies, 'model': ProxyfiedHost, 'defaults': defaults}
    return TemplateResponse(request, 'proxy.pac', template_values, content_type='application/x-ns-proxy-autoconfig')


@never_cache
def my_docs(request):
    if request.user.is_authenticated():
        set_websocket_topics(request)
    user = request.user if request.user.is_authenticated() else None
    if request.method == 'POST' and user and user.has_perm('updoc.add_uploaddoc'):
        form = UrlRewriteForm(request.POST)
        if form.is_valid():
            RewrittenUrl(user=user, src=form.cleaned_data['src'], dst=form.cleaned_data['dst']).save()
            messages.info(request, _('URL %(src)s will be rewritten as %(dst)s') % form.cleaned_data)
            return HttpResponseRedirect(reverse('updoc:my_docs'))
    else:
        form = UrlRewriteForm()
    uploads = UploadDoc.query(request).order_by('-upload_time').select_related()
    rw_urls = RewrittenUrl.query(request).order_by('src')
    template_values = {'uploads': uploads, 'title': _('My documents'), 'rw_urls': rw_urls,
                       'rw_form': form, 'editable': True, 'has_search_results': False, }
    return TemplateResponse(request, 'updoc/my_docs.html', template_values)


@csrf_exempt
@permission_required('updoc.add_uploaddoc')
def delete_url(request, url_id):
    if request.method != 'POST':
        return HttpResponseRedirect(reverse('updoc:my_docs'))
    url = get_object_or_404(RewrittenUrl.query(request), pk=url_id)
    RewrittenUrl.query(request).filter(pk=url_id).delete()
    messages.info(request, _('The replacement of %(src)s by %(dst)s has been removed') %
                  {'src': url.src, 'dst': url.dst, })
    return HttpResponseRedirect(reverse('updoc:my_docs'))


@csrf_exempt
def delete_doc(request, doc_id):
    obj = get_object_or_404(UploadDoc.query(request), id=doc_id)
    name = obj.name
    scall(request, 'updoc.delete_file', to=[SERVER], doc_id=doc_id)
    messages.info(request, _('%(doc)s will be quickly deleted') % {'doc': name})
    return HttpResponseRedirect(reverse('updoc:my_docs'))


@never_cache
@login_required(login_url='/accounts/login/')
def upload(request):
    """Index view, displaying and processing a form."""
    set_websocket_topics(request)
    if request.method == 'POST':
        form = MetadatadUploadForm(request.POST)
        if form.is_valid():
            messages.info(request, _('File successfully uploaded'))
            obj = get_object_or_404(UploadDoc.query(request), id=form.cleaned_data['pk'])
            obj.name = form.cleaned_data['name']
            for keyword in form.cleaned_data['keywords'].lower().split():
                obj.keywords.add(Keyword.get(keyword))
            obj.save()
            return HttpResponseRedirect(reverse('upload'))
        elif 'pk' in form.cleaned_data:
            obj = get_object_or_404(UploadDoc.query(request), id=form.cleaned_data['pk'])
            obj.delete()
            messages.error(request, _('Unable to upload this file'))
        else:
            messages.error(request, _('Unable to upload this file'))
    else:
        form = FileUploadForm()
    template_values = {'form': form, 'title': _('Upload a new file'), 'root_host': settings.SERVER_BASE_URL[:-1]}
    return TemplateResponse(request, 'updoc/upload.html', template_values)


@csrf_exempt
@never_cache
@permission_required('updoc.add_uploaddoc')
def upload_doc_progress(request):
    form = FileUploadForm(request.POST, request.FILES)
    if not form.is_valid():
        raise PermissionDenied
    uploaded_file = request.FILES['file']
    tmp_file = tempfile.NamedTemporaryFile(mode='wb', dir=settings.FILE_UPLOAD_TEMP_DIR, delete=False)
    chunk = uploaded_file.read(16384)
    while chunk:
        tmp_file.write(chunk)
        chunk = uploaded_file.read(16384)
    tmp_file.flush()

    basename = os.path.basename(uploaded_file.name).rpartition('.')[0]
    if basename.endswith('.tar'):
        basename = basename[:-4]
    doc = UploadDoc(name=basename, user=request.user if request.user.is_authenticated() else None,
                    uid=str(uuid.uuid1()))
    doc.save()
    scall(request, 'updoc.process_file', to=[SERVER], doc_id=doc.id, filename=tmp_file.name,
          original_filename=uploaded_file.name)
    # offer a correct name for the newly uploaded document
    form = MetadatadUploadForm(initial={'pk': doc.pk, 'name': basename, })
    template_values = {'form': form, }
    return TemplateResponse(request, 'updoc/upload_doc_progress.html', template_values)


@csrf_exempt
def upload_doc_api(request):
    user = request.user if request.user.is_authenticated() else None
    if user is None:
        return HttpResponse(_('You must be logged to upload files.\n'), status=401)
    elif request.method != 'POST':
        return HttpResponse(_('Only POST requests are allowed.\n'), status=400)
    form = UploadApiForm(request.GET)
    if not form.is_valid():
        return HttpResponse(_('You must supply filename, name and keywords in your query.\n'), status=400)
    tmp_file = tempfile.NamedTemporaryFile(mode='wb', dir=settings.FILE_UPLOAD_TEMP_DIR, delete=False)
    c = False
    chunk = request.read(32768)
    while chunk:
        tmp_file.write(chunk)
        c = True
        chunk = request.read(32768)
    tmp_file.flush()
    if not c:
        os.remove(tmp_file.name)
        return HttpResponse(_('Empty file. You must POST a valid file.\n'), status=400)
    # ok, we have the tmp file

    existing_objs = list(UploadDoc.query(request).filter(name=form.cleaned_data['name'])[0:1])
    if existing_objs:
        doc = existing_objs[0]
        doc.keywords.clear()
    else:
        doc = UploadDoc(uid=str(uuid.uuid1()), name=form.cleaned_data['name'], user=user)
        doc.save()
    for keyword in strip_split(form.cleaned_data['keywords'].lower()):
        doc.keywords.add(Keyword.get(keyword))
    scall(request, 'updoc.process_file', to=[SERVER], doc_id=doc.id, filename=tmp_file.name,
          original_filename=os.path.basename(form.cleaned_data['filename']))
    return HttpResponse(_('File successfully uploaded. It will be uncompressed and indexed.\n'), status=200)


@never_cache
def show_doc_alt(request, doc_id, path=''):
    return show_doc(request, doc_id, path=path)


@never_cache
def show_doc(request, doc_id, path=''):
    user = request.user if request.user.is_authenticated() else None
    if not user and not settings.PUBLIC_DOCS:
        raise Http404
    doc = get_object_or_404(UploadDoc, id=doc_id)
    if user:
        set_websocket_topics(request, doc)
    root_path = os.path.abspath(doc.path)
    full_path = os.path.abspath(os.path.join(root_path, path))
    if not full_path.startswith(root_path):
        raise Http404

    checked, created = LastDocs.objects.get_or_create(user=user, doc=doc)
    use_auth = reverse('updoc:show_doc', kwargs={'doc_id': doc_id, 'path': path}) == request.path
    view = 'updoc:show_doc' if use_auth else 'updoc:show_doc_alt'
    if not created:
        now = datetime.datetime.utcnow().replace(tzinfo=utc)
        LastDocs.objects.filter(user=user, doc=doc).update(count=F('count') + 1, last=now)
    editable = user and (user.is_superuser or user == doc.user)
    if not os.path.isfile(full_path):
        directory = list_directory(root_path, path, view, view_arg='path',
                                   view_kwargs={'doc_id': doc.id}, dir_view_name=view,
                                   dir_view_arg='path', dir_view_kwargs={'doc_id': doc.id}, show_files=True,
                                   show_dirs=True, show_parent=bool(path), show_hidden=False)
        template_values = {'directory': directory, 'doc': doc, 'editable': editable, 'title': str(doc),
                           'keywords': ' '.join([keyword.value for keyword in doc.keywords.all()]), 'doc_id': doc_id, }
        return TemplateResponse(request, 'updoc/list_dir.html', template_values)
    if full_path.endswith('.md'):
        view_name = 'updoc:show_doc'
        if not user:
            view_name = 'updoc:show_doc_alt'
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
            return TemplateResponse(request, 'updoc/markdown.html', template_values)
        except UnicodeDecodeError:
            pass
    return send_file_replace_url(request, full_path, allow_replace=True)


@never_cache
def show_search_results(request):
    """Index view, displaying and processing a form."""
    if request.user.is_authenticated():
        set_websocket_topics(request)
    search = DocSearchForm(request.GET)
    pattern, doc_id = '', ''
    if search.is_valid():
        pattern = search.cleaned_data['search']
        doc_id = search.cleaned_data['doc_id'] or ''
        # ElasticSearch
    es_search = []
    es_total = 0
    if request.user.is_anonymous() and not settings.PUBLIC_INDEX:
        messages.info(request, _('You must be logged to search across docs.'))
    else:
        try:
            es_search, es_total = search_archive(pattern, archive_id=doc_id)
        except ESError:
            messages.error(request, _('Unable to use indexed search.'))
    extra_obj = {}
    for obj in UploadDoc.objects.filter(id__in=set([x[0] for x in es_search])).only('id', 'name'):
        extra_obj[obj.id] = obj.name
    es_result = []
    for es in es_search:
        if es[0] not in extra_obj:
            continue
        es_result.append((extra_obj[es[0]], es[0], es[1]))
    es_result.sort(key=lambda x: x[1])
    es_data = {'results': es_result, 'total': es_total, }

    # classical search
    if not doc_id:
        docs = UploadDoc.objects.all()
        # list of UploadDoc.name, UploadDoc.id, path, UploadDoc.upload_time
        if len(pattern) > 3:
            docs = docs.filter(Q(name__icontains=pattern) | Q(keywords__value__icontains=pattern))
        else:
            docs = docs.filter(Q(name__iexact=pattern) | Q(keywords__value__iexact=pattern))
        docs = docs.distinct().select_related()
    else:
        docs = None
    template_values = {'uploads': docs, 'title': _('Search results'), 'rw_form': None,
                       'editable': False, 'es_data': es_data, 'doc_id': doc_id, }
    return TemplateResponse(request, 'updoc/my_docs.html', template_values)


@never_cache
def show_all_docs(request):
    if request.user.is_authenticated():
        set_websocket_topics(request)
    user = request.user if request.user.is_authenticated() else None
    search = DocSearchForm(request.GET)
    if request.user.is_anonymous() and not settings.PUBLIC_INDEX:
        messages.info(request, _('You must be logged to see documentations.'))
        keywords_with_counts, recent_uploads, recent_checked = [], [], []
    else:
        recent_uploads = UploadDoc.objects.order_by('name')
        recent_checked = LastDocs.objects.filter(user=user).select_related().order_by('-last')[0:40]
    if request.user.is_anonymous() and not settings.PUBLIC_BOOKMARKS:
        rss_roots = []
    else:
        rss_roots = RssRoot.objects.all().order_by('name')
    template_values = {'recent_checked': recent_checked, 'title': _('Updoc'), 'rss_roots': rss_roots,
                       'recent_uploads': recent_uploads, 'search': search, 'keywords': [],
                       'show_all_link': False,
                       'list_title': _('All documents'), }
    return TemplateResponse(request, 'updoc/index.html', template_values)


@cache_page(3600)
def docset_feed(request, doc_id, doc_name=None):
    # noinspection PyUnusedLocal
    doc_name = doc_name
    if request.user.is_anonymous() and not settings.PUBLIC_DOCS:
        raise Http404
    doc = get_object_or_404(UploadDoc, id=doc_id)
    return TemplateResponse(request, 'updoc/docset.xml', {'doc': doc}, content_type='application/xml')


@never_cache
def docset(request, doc_id):
    if request.user.is_anonymous() and not settings.PUBLIC_DOCS:
        raise Http404
    doc = get_object_or_404(UploadDoc, id=doc_id)
    assert isinstance(doc, UploadDoc)
    return send_file(doc.docset_path, mimetype='application/gzip')


@never_cache
def docset_tarix(request, doc_id):
    # noinspection PyUnusedLocal
    request = request
    # noinspection PyUnusedLocal
    doc_id = doc_id
    return HttpResponse(status=404)
