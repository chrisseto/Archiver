"""
S3 file sync
needs to export methods with a signature of:
    foo(dir_name)
    bar(file_name)
    were foo and bar will sync the given object to S3
"""
import os
import logging

from boto.s3.connection import S3Connection, Key

from registerer.settings import ACCESS_KEY, SECRET_KEY, BUCKET_NAME

logger = logging.getLogger(__name__)

connection = S3Connection(ACCESS_KEY, SECRET_KEY)
bucket = connection.get_bucket(BUCKET_NAME, validate=False)

MULTIPART_TRESHOLD = 1024 ** 2 * 500  # 500 MB
PART_SIZE_TRESHOLD = 1024 ** 2 * 250  # 500 MB


def sync_directory(dir_name):
    files_to_sync = []

    for current_dir, dirs, files in os.walk(dir_name, topdown=True):
        dirs[:] = [dir for dir in dirs if dir[0] != '.']
        for file in files:
            if file[0] != '.':
                files_to_sync.append(os.path.join(current_dir, file))

    for file in files_to_sync:
        sync_file(file)
    return True


def sync_file(file_name):
    if not bucket.get_key(file_name):
        logger.info('Pushing "{}"" to Bucket "{}"'.format(file_name, BUCKET_NAME))
        if os.path.getsize(file_name) >= MULTIPART_TRESHOLD:
            #TODO
            #mult = bucket.initiate_multipart_upload(file_name)
            pass
        else:
            pass
        k = bucket.new_key(file_name)
        k.set_contents_from_filename(file_name)
