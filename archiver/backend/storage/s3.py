"""
S3 file sync
needs to export methods with a signature of:
    foo(dir_name)
    bar(file_name)
    were foo and bar will sync the given object to S3
"""
import os
import logging

from boto.s3.connection import S3Connection

from archiver.settings import ACCESS_KEY, SECRET_KEY, BUCKET_NAME

logger = logging.getLogger(__name__)

connection = S3Connection(ACCESS_KEY, SECRET_KEY)
bucket = connection.get_bucket(BUCKET_NAME, validate=False)

MULTIPART_TRESHOLD = 1024 ** 2 * 500  # 500 MB
PART_SIZE_TRESHOLD = 1024 ** 2 * 250  # 500 MB

DOWNLOAD_LINK_LIFE = 5 * 60  # 5 Minutes


def sync_directory(src, to_dir):
    diff = src.replace(to_dir, '')
    files_to_sync = []

    for current_dir, dirs, files in os.walk(src, topdown=True):
        # dirs[:] = [dir for dir in dirs if dir[0] != '.']
        for file in files:
            # if file[0] != '.':
            files_to_sync.append(os.path.join(current_dir, file))

    for file in files_to_sync:
        sync_file(file, file.replace(diff, ''))
    return True


def sync_file(src, to_file):
    if not bucket.get_key(to_file):
        logger.info('Pushing "{}"" to Bucket "{}"'.format(to_file, BUCKET_NAME))
        if os.path.getsize(src) >= MULTIPART_TRESHOLD:
            #TODO
            #mult = bucket.initiate_multipart_upload(src)
            pass
        else:
            pass
        k = bucket.new_key(to_file)
        k.set_contents_from_filename(src)


def get_file_url(path):
    return bucket.get_key(path, headers={'Content-Disposition': 'attachment'}).generate_url(DOWNLOAD_LINK_LIFE)


def list_dir(directory, recurse=False):
    return [
        {
            'path': key.name
        }
        for key in
        bucket.list(prefix=directory, delimiter='' if recurse else '/')
    ]
