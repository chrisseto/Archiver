import os

from boto.s3.connection import S3Connection

from archiver import celery
from archiver.backend import push_file

from .utils import CUTOFF_SIZE, ensure_directory


def clone(addon):
    addon.make_dir(addon['bucket'])
    savedir = (addon.full_path(addon['bucket']), addon.path(addon['bucket']))
    return clone_s3(addon['bucket'], addon['access_key'], addon['secret_key'], *savedir)


def clone_s3(bucket, access_key, secret_key, savedir, short_dir):
    connection = S3Connection(access_key, secret_key)
    bucket = connection.get_bucket(bucket, validate=False)
    for key in bucket.list():
        if key.key[-1] != '/':
            if key.size > CUTOFF_SIZE:
                get_key.delay(savedir, short_dir, key)
            else:
                get_key(savedir, short_dir, key)


@celery.task
def get_key(savedir, short_dir, key):
    key_file = os.path.join(savedir, key.key)
    key_dir = os.path.dirname(key_file)
    ensure_directory(key_dir)
    key.get_contents_to_filename(key_file)
    push_file(key_file, os.path.join(short_dir, key.key))
