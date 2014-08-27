import logging

from .base import StorageBackEnd


logger = logging.getLogger(__name__)


class Debug(StorageBackEnd):
    '''Debug BackEnd
    This class does exactly nothing.
    '''
    USES = 'debug'

    def clean_directory(directory):
        pass

    def push_folder(self, from_loc, to):
        pass

    def get_file(self, path):
        pass

    def list_directory(self, directory):
        pass

    def upload_file(self, from_loc, to):
        pass

    def push_directory(*args):
        pass

    def list_containers(self, limit=None):
        return []
