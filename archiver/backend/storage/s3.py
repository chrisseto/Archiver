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
import httplib as http

from boto.s3.connection import S3Connection, S3ResponseError, BotoClientError

from archiver.exceptions import HTTPError
from archiver.settings import CREDENTIALS, CONTAINER_NAME

from base import StorageBackEnd
from exceptions import RemoteStorageError

logger = logging.getLogger(__name__)


class S3(StorageBackEnd):

    USES = 's3'

    def __init__(self):
        super(S3, self).__init__()
        try:
            self.connection = S3Connection(*CREDENTIALS)
            self.bucket = self.connection.get_bucket(CONTAINER_NAME)
        except (S3ResponseError, BotoClientError):
            raise RemoteStorageError('Could not connect to S3')

    def upload_file(self, path, name, directory='', retries=0):
        name = name.decode('utf-8')

        if name[0] == '/':
            name = os.path.join(directory, name[1:])
        else:
            name = os.path.join(directory, name)

        try:
            if not self.bucket.get_key(name):
                # if os.path.getsize(path) >= self.MULTIPART_THRESHOLD:
                # TODO
                k = self.bucket.new_key(name)
                logger.info('uploading "%s"' % name)
                k.set_contents_from_filename(path)
                os.remove(path)
                return True
        except:
            if retries > self.UPLOAD_RETRIES:
                raise
            self.upload_file(path, name, directory=directory, retries=retries+1)

        return False

    def get_file(self, path, name=None):
        # you can set the Content-Disposition header on your s3 file to set the downloading filename:
        # Content-Disposition: attachment; filename=foo.bar
        # http://stackoverflow.com/questions/2611432/amazon-s3-change-file-download-name

        key = self.bucket.get_key(path)

        if not key:
            raise HTTPError(http.NOT_FOUND)

        if '.json' in path:
            ret = json.loads(key.get_contents_as_string())
            return jsonify(ret)

        if name:
            content_dispo = 'attachment; filename="{}"'.format(name)
        else:
            content_dispo = 'attachment'

        return key.generate_url(self.DOWNLOAD_LINK_LIFE, response_headers={'response-content-disposition': content_dispo}), {}

    def list_directory(self, directory, recurse=False):
        return [
            key.name
            for key in
            self.bucket.list(prefix=directory, delimiter='' if recurse else '/')
        ]
