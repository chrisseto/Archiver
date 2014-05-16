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
from base import BackEnd
from debug import Debug
from s3 import S3
