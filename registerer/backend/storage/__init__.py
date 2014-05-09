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
from . import s3

push_directory = s3.sync_directory
push_file = s3.sync_file


def clean_directory(dir):
    pass
