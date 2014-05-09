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
from . import s3


push_file = s3.sync_file


def push_directory(directory):
    if s3.sync_directory(directory):
        clean_directory(directory)
        return True
    return False


def clean_directory(directory):
    rmtree(directory)
