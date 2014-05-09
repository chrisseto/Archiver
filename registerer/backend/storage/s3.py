"""
S3 file sync
needs to export methods with a signature of:
    foo(dir_name)
    bar(file_name)
    were foo and bar will sync the given object to S3
"""
import os

from boto.s3.connection import S3Connection, Key

from registerer.settings import ACCESS_KEY, SECRET_KEY, BUCKET_NAME


connection = S3Connection(ACCESS_KEY, SECRET_KEY)
bucket = connection.get_bucket(BUCKET_NAME, validate=False)


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
    k = bucket.new_key(file_name)
    k.set_contents_from_filename(file_name)
