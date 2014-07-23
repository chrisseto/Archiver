import os
import json
import logging
import httplib as http
from urllib import quote

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
        pyrax.set_credentials(settings.USERNAME, api_key=settings.PASSWORD)
        self.connection = pyrax.cloudfiles
        self.connection.set_temp_url_key()
        self.container = self.connection.get_container(settings.CONTAINER_NAME)

    def upload_file(self, path, name, directory=''):
        name = os.path.join(directory, name)
        if not self.container.get_object(name):
            logger.info('uploading "%s"' % name)
            self.container.upload_file(path, obj_name=name)
            os.remove(path)
            return True
        return False

    def get_file(self, path, name=None):
        obj = self.container.get_object(path)

        if not obj:
            raise HTTPError(http.NOT_FOUND)

        if '.json' in path:
            ret = json.loads(obj.fetch())
            return jsonify(ret)

        temp_url = obj.get_temp_url(self.DOWNLOAD_LINK_LIFE)

        if name:
            return redirect('%s&filename=%s' % (temp_url, quote(name)))

        return redirect(temp_url)

    def list_directory(self, directory, recurse=False):
        return [
            obj.name for obj in
            self.connection.get_objects(prefix=directory, delimiter='' if recurse else '/')
        ]
