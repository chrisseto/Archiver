import re
import os
import abc
import copy
import json
import logging
import tempfile
try:
    import httplib as http  # Python 2
except ImportError:
    import http.client as http  # Python 3
from shutil import rmtree

from archiver import settings
from archiver.util import parchive
from archiver.exceptions import HTTPError

logger = logging.getLogger(__name__)


class StorageBackEnd(object):
    __metaclass__ = abc.ABCMeta

    USES = None

    UPLOAD_RETRIES = 3

    DELIMITER = '.manifest.json'

    DOWNLOAD_LINK_LIFE = 60 * settings.DOWNLOAD_LINK_LIFE
    MULTIPART_THRESHOLD = 1024 ** 2 * settings.MULTIPART_THRESHOLD

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
        # Dont store name or path with generic file data
        try:
            del clone['path']
        except:
            pass

        try:
            del clone['name']
        except:
            pass

        return self.push_json(clone, os.path.join(settings.METADATA_DIR, name))

    def push_directory_structure(self, final, parent_id=''):
        prefix = os.path.join(settings.DIRSTRUCT_DIR, parent_id, final['metadata']['id'])

        self.push_json(final, 'manifest', directory=prefix)

        for service in final['services'].values():
            self.push_json(service, 'manifest', os.path.join(prefix, service['service']))
            service_prefix = os.path.join(prefix, service['service'], service['resource'])

            for fid in service['files']:
                self.push_json(fid, fid['path'], directory=service_prefix)

        for child in final['children'].values():
            self.push_directory_structure(child, final['metadata']['id'])

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
        """Filter a directory listing via regex
        :param str filter a regex string
        :param int limit The max amount of results to return
        :param str remove A string to trim from the results
        :param str directory The directory to search in
        """
        #TODO Pagination?
        return [
            self.remove(container, remove)
            for container in
            self.list_directory(directory)
            if re.search(filter, container)
        ][:limit]

    def push_file(self, path, name, force_parity=settings.IGNORE_PARITIY_SIZE_LIMIT):
        # Parity files create redundant backups that can be used to recover ~10% of file corruption
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
        try:
            return self.get_file('{}{}{}'.format(settings.MANIFEST_DIR, cid, self.DELIMITER))
        except Exception:
            # This will swallow all errors
            # Tread lightly
            # TODO Ensure that get_file will only raise one type of error
            raise HTTPError(http.NOT_FOUND)

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
