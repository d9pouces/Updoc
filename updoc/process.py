import os
import shutil
import tarfile
import tempfile
import zipfile

from django.db.models import F
from django.utils.text import slugify

from djangofloor.utils import ensure_dir

from updoc.docset import Docset
from updoc.indexation import index_archive
from updoc.models import UploadDoc

__author__ = 'Matthieu Gallet'


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
    temp_file.flush()
    temp_file.seek(0)
    return temp_file


def copy_to_path(in_fd, dst_path: str):
    """Copy the content of file descriptor to the given path.

    Create parent directory if needed.

    :param in_fd: any file object, open in read-binary mode
    :param dst_path:
    """
    with open_with_dir(dst_path) as out_fd:
        for data in iter(lambda: in_fd.read(32768), b''):
            out_fd.write(data)


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


def zip_archive(doc: UploadDoc):
    ensure_dir(doc.zip_path)
    arc_root = slugify(doc.name)
    with open(doc.zip_path, 'wb') as tmp_file:
        compression_file = zipfile.ZipFile(tmp_file, mode='w', compression=zipfile.ZIP_DEFLATED)
        path = doc.path
        documents_dir = os.path.join(path, 'Contents', 'Resources', 'Documents')
        plist_path = os.path.join(path, 'Contents', 'Info.plist')
        if os.path.isdir(documents_dir) and os.path.isfile(plist_path):
            path = documents_dir

        for (root, dirnames, filenames) in os.walk(path):
            for filename in filenames:
                full_path = os.path.join(root, filename)
                arcname = os.path.join(arc_root, os.path.relpath(full_path, doc.path))
                compression_file.write(full_path, arcname)
        compression_file.close()


def process_uploaded_file(doc: UploadDoc, temp_file, original_filename: str):
    """
    * Clean previous content if needed
    * Uncompress content
    * Index content

    :param doc:
    :param temp_file: file descriptor
    :param original_filename: nom d'origine du fichier
    """
    assert isinstance(doc, UploadDoc)
    destination_root = doc.uncompressed_root
    doc_id = doc.id
    doc_uid = doc.uid
    UploadDoc.objects.filter(id=doc_id).update(path=destination_root, version=F('version') + 1)
    doc.path = destination_root
    doc.version += 1
    # first, we clean previous index and data
    doc.clean_archive()

    # ok, let's go to decompress
    destination_root += os.path.sep
    if original_filename[-7:] in ('.tar.gz', '.tar.xz') or original_filename[-8:] == '.tar.bz2'\
            or original_filename[-4:] in ('.tar', '.tbz', '.tgz', '.txz'):
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

        obj_to_extract = [zipped_obj for zipped_obj in zip_file.infolist()
                          if os.path.join(doc_uid, zipped_obj.filename).startswith(doc_uid)]
        common_prefix = os.path.sep.join(os.path.commonprefix([obj_.filename.split(os.path.sep)
                                                               for obj_ in obj_to_extract]))
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
    # prepare docset
    Docset(doc).prepare()
    zip_archive(doc)
    return doc
