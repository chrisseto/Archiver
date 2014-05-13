import os

from boto.s3.connection import S3Connection

from registerer import celery
from registerer.backend import push_file

from .utils import CUTOFF_SIZE


def clone_s3(addon):
    connection = S3Connection(addon['access_key'], addon['secret_key'])
    bucket = connection.get_bucket(addon['bucket'], validate=False)
    for key in bucket.list():
        if key.size > CUTOFF_SIZE:
            get_key.delay(addon, key)
        else:
            get_key(addon, key)


@celery.task
def get_key(addon, key):
    bucket = addon['bucket']
    dest = os.path.join(addon.full_path(bucket), key.key)
    key.get_contents_to_filename(dest)
    push_file(dest, addon.path(os.path.join(bucket, key.key)))


#export as clone
clone = clone_s3
