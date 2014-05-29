"""
S3 file sync
needs to export methods with a signature of:
    foo(dir_name)
    bar(file_name)
    were foo and bar will sync the given object to S3
"""
import os
import json
import logging

from base import StorageBackEnd

from boto.s3.connection import S3Connection, S3ResponseError, BotoClientError

from archiver.settings import ACCESS_KEY, SECRET_KEY, BUCKET_NAME

from exceptions import RemoteStorageError

logger = logging.getLogger(__name__)


class S3(StorageBackEnd):

    MULTIPART_THRESHOLD = 1024 ** 2 * 500  # 500 MB
    PART_SIZE_THRESHOLD = 1024 ** 2 * 250  # 250 MB
    DOWNLOAD_LINK_LIFE = 5 * 60  # 5 Minutes
    USES = 's3'

    def __init__(self):
        super(S3, self).__init__()
        try:
            self.connection = S3Connection(ACCESS_KEY, SECRET_KEY)
            self.bucket = self.connection.get_bucket(BUCKET_NAME)
        except (S3ResponseError, BotoClientError):
            raise RemoteStorageError('Could not connect to S3')

    def push_file(self, path, name):
        if not self.bucket.get_key(name):
            # if os.path.getsize(path) >= self.MULTIPART_THRESHOLD:
            # TODO
            k = self.bucket.new_key(name)
            k.set_contents_from_filename(path)

    def get_file(self, path):
        return self.bucket.get_key(path, headers={'Content-Disposition': 'attachment'}).generate_url(self.DOWNLOAD_LINK_LIFE)

    def list_directory(self, directory, recurse=False):
        return [
            {
                'path': key.name
            }
            for key in
            self.bucket.list(prefix=directory, delimiter='' if recurse else '/')
        ]
