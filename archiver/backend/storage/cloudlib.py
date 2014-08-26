import os
import json
import logging
import httplib as http

from libcloud.storage.providers import get_driver

from archiver.settings import LIBCLOUD_DRIVER, CREDENTIALS, CONTAINER_NAME
from archiver.exceptions import HTTPError

from base import StorageBackEnd
from exceptions import RemoteStorageError


logger = logging.getLogger(__name__)


class LibCloudBackend(StorageBackEnd):
    USES = 'libcloud'

    def __init__(self):
        super(LibCloudBackend, self).__init__()
        # try:
        self.driver_cls = get_driver(LIBCLOUD_DRIVER)
        self.driver = self.driver_cls(*CREDENTIALS)
        self.container = self.driver.get_container(CONTAINER_NAME)
        # except:
            # raise RemoteStorageError('TODO')

    def upload_file(self, path, name, directory='', retries=0):
        name = name.decode('utf-8')

        if name[0] == '/':
            name = os.path.join(directory, name[1:])
        else:
            name = os.path.join(directory, name)
        try:
            if not self.container.get_object(name):
                logger.info('uploading "%s"' % name)
                self.container.upload_object(path, name)
        except:
            if retries > self.UPLOAD_RETRIES:
                raise

    def get_file(self, path, name=None):
        key = self.container.get_object(path)

        if not key:
            raise HTTPError(http.NOT_FOUND)

        fobj = key.as_stream()

        if '.json' in path:
            ret = json.loads(''.join(fobj))
            return jsonify(ret)

        headers = {
            #wwsd
            'Content-Disposition': 'attachment;%s' %
            ('filename="%s"' % name if name else '')

        }

        return fobj, headers

    def list_directory(self, directory, recurse=False):
        # Warning, This method is crazy slow. WILL NOT SCALE
        # libcloud provides no way to filter search results on their side
        return [
            key.name.replace(directory, '')
            for key in
            self.container.list_objects()
            if directory in key.name
        ]
