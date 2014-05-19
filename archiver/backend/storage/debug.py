import logging
from base import BackEnd


logger = logging.getLogger(__name__)


class Debug(BackEnd):
    '''Debug BackEnd
    This class does exactly nothing.
    '''

    def clean_directory(directory):
        pass

    def push_folder(self, from_loc, to):
        pass

    def get_file(self, path):
        pass

    def list_directory(self, directory):
        pass

    def push_file(self, from_loc, to):
        pass

    def push_directory(*args):
        pass
