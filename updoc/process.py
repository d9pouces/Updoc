import uuid
import zipfile
from django.core.files.uploadedfile import UploadedFile

import shutil

import os
import tarfile
import tempfile
from django.conf import settings
from django.http import HttpRequest
from djangofloor.decorators import SignalRequest

from updoc.indexation import index_archive, delete_archive
from updoc.models import UploadDoc


__author__ = 'flanker'


def open_with_dir(dst_path: str, mode='wb'):
    if not os.path.isdir(os.path.dirname(dst_path)):
        os.makedirs(os.path.dirname(dst_path))
    return open(dst_path, mode=mode)


def get_tempfile(uploaded_file):
    temp_file = tempfile.NamedTemporaryFile()
    chunk = uploaded_file.read(16384)
    while chunk:
        temp_file.write(chunk)
        chunk = uploaded_file.read(16384)
    temp_file.seek(0)
    return temp_file


def copy_to_path(in_fd, dst_path: str):
    """Copy the content of file descriptor to the given path.

    Create parent directory if needed.

    :param in_fd: any file object, open in read-binary mode
    :param dst_path:
    """
    with open_with_dir(dst_path) as out_fd:
        data = in_fd.read(32768)
        while data:
            out_fd.write(data)
            data = in_fd.read(32768)


def clean_archive(root_path: str):
    """Remove unwanted files (like .svn, .git, …)

    :param root_path:
    """
    for (root, dirnames, filenames) in os.walk(root_path):
        index = 0
        while index < len(dirnames):
            dirname = dirnames[index]
            if dirname in {'.svn', '.git', '.hg', '__MACOSX', '__pycache__'}:
                try:
                    shutil.rmtree(os.path.join(root_path, root, dirname))
                except IOError:
                    pass
                del dirnames[index]
            else:
                index += 1


def process_new_file(uploaded_file: UploadedFile, request: HttpRequest, obj: UploadDoc=None):
    """takes a UploadedFile object and returns a saved UploadDoc object

    """
    if obj is None:
        obj = UploadDoc(uid=str(uuid.uuid1()))
    # noinspection PyUnresolvedReferences
    obj.user = request.user if request.user.is_authenticated() else None
    basename = os.path.basename(uploaded_file.name)
    root = os.path.join(settings.MEDIA_ROOT, 'docs', obj.uid[0:2], obj.uid)
    obj.path = root
    try:
        obj.name = basename
        root += '/'

        if basename[-7:] in ('.tar.gz', '.tar.xz') or basename[-8:] == '.tar.bz2' or \
                basename[-4:] in ('.tar', '.tbz', '.tgz', '.txz'):
            temp_file = get_tempfile(uploaded_file)
            tar_file = tarfile.open(name=basename, mode='r:*', fileobj=temp_file)
            names = filter(lambda name_: os.path.join(obj.uid, name_).startswith(obj.uid), tar_file.getnames())
            common_prefix = '/'.join(os.path.commonprefix([name_.split('/') for name_ in names]))
            common_prefix_len = len(common_prefix)
            for member in tar_file.getmembers():
                if not os.path.join(obj.uid, member.name).startswith(obj.uid):
                    continue
                dst_path = root + member.name[common_prefix_len:]
                if member.isdir():
                    # noinspection PyArgumentList
                    os.makedirs(dst_path, mode=0o777, exist_ok=True)
                elif member.issym():
                    if not os.path.join(obj.uid, member.linkname).startswith(obj.uid):
                        continue
                    os.symlink(root + member.linkname[common_prefix_len:], dst_path)
                elif member.isfile():
                    copy_to_path(tar_file.extractfile(member), dst_path)
            tar_file.close()
            temp_file.close()
        elif basename[-4:] == '.zip':
            temp_file = get_tempfile(uploaded_file)
            zip_file = zipfile.ZipFile(temp_file, mode='r')
            uid = obj.uid
            names = list(filter(lambda zip_: os.path.join(uid, zip_.filename).startswith(uid), zip_file.infolist()))
            common_prefix = '/'.join(os.path.commonprefix([obj_.filename.split('/') for obj_ in names]))
            common_prefix_len = len(common_prefix)
            for obj_ in names:
                if obj_.filename[-1:] == '/':
                    continue
                copy_to_path(zip_file.open(obj_.filename), root + obj_.filename[common_prefix_len:])
            zip_file.close()
            temp_file.close()
        else:
            with open_with_dir(os.path.join(root, basename)) as out_fd:
                for chunk in uploaded_file.chunks():
                    out_fd.write(chunk)
        clean_archive(root)
        obj.save()
        index_archive(obj.id, root)
    except Exception as e:
        shutil.rmtree(root)
        raise e
    return obj



def process_uploaded_file(doc: UploadDoc, temp_file, original_filename: str, destination_root: str):
    """
    * Clean previous content if needed
    * Uncompress content
    * Index content

    :param doc:
    :param temp_file:
    :param original_filename:
    :param destination_root:
    """
    doc_id = doc.id
    doc_uid = doc.uid
    UploadDoc.objects.filter(id=doc_id).update(path=destination_root)
    # first, we clean previous index and data
    doc.clean_archive()

    # ok, let's go to decompress
    destination_root += os.path.sep
    if original_filename[-7:] in ('.tar.gz', '.tar.xz') or original_filename[-8:] == '.tar.bz2' or original_filename[-4:] in ('.tar', '.tbz', '.tgz', '.txz'):
        tar_file = tarfile.open(name=original_filename, mode='r:*', fileobj=temp_file)
        names = [name_ for name_ in tar_file.getnames() if os.path.join(doc_uid, name_).startswith(doc_uid)]
        common_prefix = os.path.sep.join(os.path.commonprefix([name_.split(os.path.sep) for name_ in names]))
        common_prefix_len = len(common_prefix)
        for member in tar_file.getmembers():
            if not os.path.join(doc_uid, member.name).startswith(doc_uid):
                continue
            dst_path = destination_root + member.name[common_prefix_len:]
            if member.isdir():
                os.makedirs(dst_path, mode=0o777, exist_ok=True)
            elif member.issym():
                if not os.path.join(doc_uid, member.linkname).startswith(doc_uid):
                    continue
                os.symlink(destination_root + member.linkname[common_prefix_len:], dst_path)
            elif member.isfile():
                copy_to_path(tar_file.extractfile(member), dst_path)
        tar_file.close()
    elif original_filename[-4:] == '.zip':
        zip_file = zipfile.ZipFile(temp_file, mode='r')

        obj_to_extract = [zipped_obj for zipped_obj in zip_file.infolist() if os.path.join(doc_uid, zipped_obj.filename).startswith(doc_uid)]
        common_prefix = os.path.sep.join(os.path.commonprefix([obj_.filename.split(os.path.sep) for obj_ in obj_to_extract]))
        common_prefix_len = len(common_prefix)
        for zipped_obj in obj_to_extract:
            if zipped_obj.filename[-1:] == os.path.sep:
                continue
            copy_to_path(zip_file.open(zipped_obj.filename), destination_root + zipped_obj.filename[common_prefix_len:])
        zip_file.close()
    else:
        copy_to_path(temp_file, os.path.join(destination_root, original_filename))
    # remove unwanted files
    clean_archive(destination_root)
    # index
    index_archive(doc_id, destination_root)
