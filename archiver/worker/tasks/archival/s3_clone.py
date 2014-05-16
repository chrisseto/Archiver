from boto.s3.connection import S3Connection

from archiver import celery
from archiver.backend import push_file

from .utils import CUTOFF_SIZE, build_directories


def clone(addon):
    dirinfo = {
        'tempdir': addon.parent.TEMP_DIR,
        'prefix': addon.path(addon['bucket'])
    }
    addon.make_dir(addon['bucket'])
    return clone_s3(addon['bucket'], addon['access_key'], addon['secret_key'], dirinfo)


def clone_s3(bucket, access_key, secret_key, dirinfo):
    connection = S3Connection(access_key, secret_key)
    bucket = connection.get_bucket(bucket, validate=False)
    for key in bucket.list():
        if key.key[-1] != '/':
            if key.size > CUTOFF_SIZE:
                get_key.delay(key, dirinfo)
            else:
                get_key(key, dirinfo)


@celery.task
def get_key(key, dirinfo):
    path, save_loc = build_directories(dirinfo, key.key)
    key.get_contents_to_filename(path)
    push_file(path, save_loc)
