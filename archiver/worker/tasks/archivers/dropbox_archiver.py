from dropbox.client import DropboxClient

from archiver import celery
from archiver.backend import store

from base import ServiceArchiver


class DropboxArchiver(ServiceArchiver):
    CLONES = 'dropbox'
    RESOURCE = 'folder'

    def __init__(self, addon):
        self.client = DropboxClient(addon['access_token'])
        self.folder_name = addon['folder']
        super(DropboxArchiver, self).__init__(addon)

    def clone(self):
        pass

    @celery.task
    def recurse(self, contents):
        for item in contents:
            if item['is_dir']:
                if item['bytes'] > self.CUTOFF_SIZE:
                    self.recurse.delay(contents)
                else:
                    self.recurse(contents)
            if item['bytes'] > self.CUTOFF_SIZE:
                self.fetch.delay(item['path'])
            else:
                self.fetch(item['path'])

    @celery.task
    def fetch(self, path):
        fobj = self.client.get_file(path)

        path, save_loc = self.build_directories(path[1:])  # Remove beginning /

        self.chunked_save(fobj, path)
        store.push_file(path, save_loc)
