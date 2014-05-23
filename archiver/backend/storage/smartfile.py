
import logging

from base import StorageBackEnd

from archiver.settings import smartfile_ACCESS_KEY, smartfile_SECRET_KEY

from exceptions import RemoteStorageError

from smartfile import OAuthClient

logger = logging.getLogger(__name__)


class Smartfile(StorageBackEnd):

    def __init__(self):
        super(Smartfile, self).__init__()
        try:
            self.api = OAuthClient(smartfile_ACCESS_KEY, smartfile_SECRET_KEY)
            self.api.get_request_token()
            client_verification = raw_input("What was the verification? :")
            self.api.get_access_token(None, client_verification)
        except :
            raise RemoteStorageError('Could not connect to smartfile')

    def push_file(self, from_loc, to):
        if not self.api.get_request_token():
            logger.info("In your browser, go to: {}".format(self.api.get_authorization_url()))
            k = self.api.get_request_token()
            k.post(self.api.get('/ping'), from_loc)

    def get_file(self, path):
        return self.api.get(path, headers={'Content-Disposition': 'attachment'}).generate_url(self.api.get_authorization_url())

    def list_directory(self, directory, recurse=False):
        return [
            {
                'path': key.name
            }
            for key in
            self.api.list(prefix=directory, delimiter='' if recurse else '/')
        ]