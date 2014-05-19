"""
S3 file sync
needs to export methods with a signature of:
    foo(dir_name)
    bar(file_name)
    were foo and bar will sync the given object to S3
"""
import os
import logging

from base import BackEnd

from boto.s3.connection import S3Connection, S3ResponseError, BotoClientError

from archiver.settings import ACCESS_KEY, SECRET_KEY, BUCKET_NAME

from exceptions import RemoteStorageError

logger = logging.getLogger(__name__)


class S3(BackEnd):

    MULTIPART_THRESHOLD = 1024 ** 2 * 500  # 500 MB
    PART_SIZE_THRESHOLD = 1024 ** 2 * 250  # 250 MB
    DOWNLOAD_LINK_LIFE = 5 * 60  # 5 Minutes

    def __init__(self):
        super(S3, self).__init__()
        try:
            self.connection = S3Connection(ACCESS_KEY, SECRET_KEY)
            self.bucket = self.connection.get_bucket(BUCKET_NAME)
        except (S3ResponseError, BotoClientError):
            raise RemoteStorageError('Could not connect to S3')

    def push_file(self, from_loc, to):
        if not self.bucket.get_key(to):
            logger.info('Pushing "{}"" to Bucket "{}"'.format(to, BUCKET_NAME))
            if os.path.getsize(from_loc) >= self.MULTIPART_THRESHOLD:
                # TODO
                #mult = bucket.initiate_multipart_upload(src)
                pass
            else:
                pass
            k = self.bucket.new_key(to)
            k.set_contents_from_filename(from_loc)

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
