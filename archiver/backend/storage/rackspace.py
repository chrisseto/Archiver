import os
import json
import logging
import httplib as http


import pyrax
import pyrax.exceptions as exc

from flask import redirect, jsonify

from archiver import settings
from archiver.exceptions import HTTPError

from base import StorageBackEnd
from exceptions import RemoteStorageError

logger = logging.getLogger(__name__)


class RackSpace(StorageBackEnd):

    MULTIPART_THRESHOLD = 1024 ** 2 * 500  # 500 MB
    PART_SIZE_THRESHOLD = 1024 ** 2 * 250  # 250 MB
    DOWNLOAD_LINK_LIFE = 5 * 60  # 5 Minutes
    USES = 'rackspace'

    def __init__(self):
        super(RackSpace, self).__init__()
        try:
            self.connection = pyrax.cloudfiles
            self.container = self.connection.get_container(settings.CONTAINER_NAME)
        except (S3ResponseError, BotoClientError):
            raise RemoteStorageError('Could not connect to S3')

    def upload_file(self, path, name, directory=''):
        name = os.path.join(directory, name)
        if not self.bucket.get_key(name):
            logger.info('uploading "%s"' % name)
            self.connection.upload_file(name, path)
            os.remove(path)
            return True
        return False

    def get_file(self, path, name=None):
        # you can set the Content-Disposition header on your s3 file to set the downloading filename:
        # Content-Disposition: attachment; filename=foo.bar
        # http://stackoverflow.com/questions/2611432/amazon-s3-change-file-download-name

        obj = self.container.get_object(path)

        if not obj:
            raise HTTPError(http.NOT_FOUND)

        if '.json' in path:
            ret = json.loads(obj.fetch())
            return jsonify(ret)

        return redirect(obj.get_temp_url(self.DOWNLOAD_LINK_LIFE))

    def list_directory(self, directory, recurse=False):
        return [
            key.name
            for key in
            self.bucket.list(prefix=directory, delimiter='' if recurse else '/')
        ]
