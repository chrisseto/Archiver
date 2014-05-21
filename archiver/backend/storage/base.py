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

    def push_directory(self, from_loc, to):
        diff = from_loc.replace(to, '')
        for current_dir, dirs, files in os.walk(from_loc, topdown=True):
            for f in files:
                f = os.path.join(current_dir, f)
                self.push_file(f, f.replace(diff, ''))
        self.clean_directory(from_loc)
        return True

    def get_file(self, path):
        raise NotImplementedError('No get_file method')

    def list_directory(self, directory):
        raise NotImplementedError('No list_directory method')

    def push_file(self, from_loc, to):
        raise NotImplementedError('No push_file method')

    def get_metadata(self, id):
        raise NotImplementedError('Not get_metadata')
