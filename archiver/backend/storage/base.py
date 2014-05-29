import os
import logging
from shutil import rmtree

logger = logging.getLogger(__name__)


class StorageBackEnd(object):

    USES = None

    def __init__(self):
        logger.debug('Loading backend {}'.format(self.__class__.__name__))

    def clean_directory(self, directory):
        rmtree(directory)

    def push_directory(self, dir_path):
        for current_dir, dirs, files in os.walk(dir_path, topdown=True):
            for f in files:
                full_path = os.path.join(current_dir, f)
                yield full_path, self.push_file(full_path)
        self.clean_directory(dir_path)

    def push_file(self, path, name):
        pass

    def push_json(self, blob, name):
        pass

    def get_file(self, path):
        raise NotImplementedError('No get_file method')

    def list_directory(self, directory):
        raise NotImplementedError('No list_directory method')

    def get_metadata(self, id):
        raise NotImplementedError('Not get_metadata')

    def upload_file(self, path, metadata):
        raise NotImplementedError()
