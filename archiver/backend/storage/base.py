import re
import os
import copy
import json
import logging
import tempfile
from shutil import rmtree

logger = logging.getLogger(__name__)


class StorageBackEnd(object):

    USES = None

    FILES_DIR = 'Files/'
    MANIFEST_DIR = 'Manifests/'
    METADATA_DIR = 'File Metadata/'
    DIRSTRUCT_DIR = 'Directory Structures/'

    DELIMITER = '.manifest.json'

    FILTER_SERVICES = r'^[^\.]+\.{}\.json$'
    FILTER_CONTAINER_SERVICE = r'^{}\.{}\.json$'
    FILTER_CONTAINERS = r'^[^\.]+\.manifest\.json$'

    def __init__(self):
        logger.debug('Loading backend {}'.format(self.__class__.__name__))

    @classmethod
    def remove(cls, string, blob):
        if isinstance(blob, list):
            for i in blob:
                string = cls.remove(string, i)
            return string
        return string.replace(blob, '')

    def clean_directory(self, directory):
        rmtree(directory)

    def push_directory(self, dir_path):
        for current_dir, dirs, files in os.walk(dir_path, topdown=True):
            for f in files:
                full_path = os.path.join(current_dir, f)
                yield full_path, self.push_file(full_path)
        self.clean_directory(dir_path)

    def push_json(self, blob, name, directory=''):
        fd, path = tempfile.mkstemp()
        with os.fdopen(fd, 'w') as json_file:
            json_file.write(json.dumps(blob))
        return self.push_file(path, '{}.json'.format(name), dir=directory)

    def push_manifest(self, blob, name):
        self.push_json(blob, '{}.manifest'.format(name), directory=self.MANIFEST_DIR)

    def push_metadata(self, blob, name):
        clone = copy.deepcopy(blob)
        try:
            del clone['path']
            del clone['name']
        except:
            pass
        return self.push_json(clone, os.path.join(self.METADATA_DIR, name))

    def push_directory_structure(self, final):
        prefix = os.path.join(self.DIRSTRUCT_DIR, final['metadata']['id'])
        self.push_json(final, 'manifest', directory=prefix)

        for service in final['services'].values():
            self.push_json(service, 'manifest', os.path.join(prefix, service['service']))
            sprefix = os.path.join(prefix, service['service'], service['resource'])

            for fid in service['files']:
                self.push_json(fid, fid['path'], directory=sprefix)

    def list_containers(self, limit=None):
        return self._filter(
            self.FILTER_CONTAINERS,
            limit=limit,
            directory=self.MANIFEST_DIR,
            remove=[self.DELIMITER, self.MANIFEST_DIR])

    def list_container_service(self, cid, service, limit=None):
        return self._filter(
            self.FILTER_CONTAINER_SERVICES.format(cid, service),
            limit=limit,
            directory=self.MANIFEST_DIR,
            remove=self.DELEMITER)

    def _filter(self, filter, limit=None, remove='', directory=''):
        #TODO Pagination?
        return [
            self.remove(container, remove)
            for container in
            self.list_directory(directory)
            if re.search(filter, container)
        ][:None]

    def get_container(self, cid):
        return self.get_file('{}{}{}'.format(self.MANIFEST_DIR, cid, self.DELIMITER))

    def get_container_service(self, cid, service):
        return self.get_file('{}{}.{}{}'.format(self.MANIFEST_DIR, cid, service, self.DELIMITER))

    def push_file(self, path, name, dir=FILES_DIR):
        raise NotImplementedError('No push_file method')

    def get_file(self, path):
        raise NotImplementedError('No get_file method')

    def list_directory(self, directory):
        raise NotImplementedError('No list_directory method')

    def get_metadata(self, id):
        raise NotImplementedError('Not get_metadata')

    def upload_file(self, path, metadata):
        raise NotImplementedError()
