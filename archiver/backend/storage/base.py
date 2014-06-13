import re
import os
import abc
import copy
import json
import logging
import tempfile
from shutil import rmtree

from archiver import settings
from archiver import parchive

logger = logging.getLogger(__name__)


class StorageBackEnd(object):
    __metaclass__ = abc.ABCMeta

    USES = None

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

    def push_json(self, blob, name, directory=''):
        fd, path = tempfile.mkstemp()
        with os.fdopen(fd, 'w') as json_file:
            json_file.write(json.dumps(blob))
        return self.upload_file(path, '{}.json'.format(name), directory=directory)

    def push_manifest(self, blob, name):
        self.push_json(blob, '{}.manifest'.format(name), directory=settings.MANIFEST_DIR)

    def push_metadata(self, blob, name):
        clone = copy.deepcopy(blob)
        try:
            del clone['path']
            del clone['name']
        except:
            pass
        return self.push_json(clone, os.path.join(settings.METADATA_DIR, name))

    def push_directory_structure(self, final):
        prefix = os.path.join(settings.DIRSTRUCT_DIR, final['metadata']['id'])
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
            directory=settings.MANIFEST_DIR,
            remove=[self.DELIMITER, settings.MANIFEST_DIR])

    def list_container_service(self, cid, service, limit=None):
        return self._filter(
            self.FILTER_CONTAINER_SERVICES.format(cid, service),
            limit=limit,
            directory=settings.MANIFEST_DIR,
            remove=settings.DELEMITER)

    def _filter(self, filter, limit=None, remove='', directory=''):
        #TODO Pagination?
        return [
            self.remove(container, remove)
            for container in
            self.list_directory(directory)
            if re.search(filter, container)
        ][:None]

    def push_file(self, path, name, force_parity=settings.IGNORE_PARITIY_SIZE_LIMIT):
        if settings.CREATE_PARITIES:
            self.build_parities(path, name, force=force_parity)
        else:
            logger.info('Skipping parity creation for %s' % path)
        return self.upload_file(path, name, directory=settings.FILES_DIR)

    def build_parities(self, path, name, force=False):
        logger.info('Creating parities for %s' % path)
        parities = parchive.create(path, name, force=force)
        if parities:
            metadata = parchive.build_metadata(parities)
            self.push_metadata(metadata, '%s.par2' % name)
            for parity in parities:
                self.upload_file(parity, os.path.basename(parity), directory=settings.PARITY_DIR)

    def get_container(self, cid):
        return self.get_file('{}{}{}'.format(settings.MANIFEST_DIR, cid, self.DELIMITER))

    def get_container_service(self, cid, service):
        return self.get_file('{}{}.{}{}'.format(settings.MANIFEST_DIR, cid, service, self.DELIMITER))

    @abc.abstractmethod
    def upload_file(self, path, name, directory=''):
        raise NotImplementedError('No upload_file method')

    @abc.abstractmethod
    def list_directory(self, directory, recurse=False):
        raise NotImplementedError('No list_directory method')

    @abc.abstractmethod
    def get_file(self, path, name=None):
        raise NotImplementedError('No get_file')
