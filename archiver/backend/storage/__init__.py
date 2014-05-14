"""
Module: Storage
A dynamic storage module
Will handle uploading a cloned project to our choice of storage service
Implements four (4) methods:
    push_directory
    push_file
    get_directory
    get_file
"""
from shutil import rmtree

from . import s3, exceptions


push_file = s3.sync_file
list_directory = s3.list_dir


def push_directory(src, to_dir):
    try:
        if s3.sync_directory(src, to_dir):
            clean_directory(src)
            return True
    except Exception:
        raise exceptions.RemoteStorageError()


def clean_directory(directory):
    rmtree(directory)


def get_file(name):
    return s3.get_file_url(name)
