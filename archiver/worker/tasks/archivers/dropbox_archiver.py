from dropbox.client import DropboxClient

from celery.contrib.methods import task_method

from archiver import celery
from archiver.backend import store

from base import ServiceArchiver


# TODO Should The entire path be stored?
class DropboxArchiver(ServiceArchiver):
    ARCHIVES = 'dropbox'
    RESOURCE = ''  # Dropbox will include the entire path

    def __init__(self, service):
        self.client = DropboxClient(service['access_token'])
        self.folder_name = service['folder']
        super(DropboxArchiver, self).__init__(service)

    def clone(self):
        start_folder = self.client.metadata(self.folder_name)
        self.recurse(start_folder)

    @celery.task(filter=task_method)
    def recurse(self, contents):
        for item in contents['contents']:
            if item['is_dir']:
                new_contents = self.client.metadata(item['path'])
                if item['bytes'] > self.CUTOFF_SIZE:
                    self.recurse.delay(new_contents)
                else:
                    self.recurse(new_contents)
            else:
                if item['bytes'] > self.CUTOFF_SIZE:
                    self.fetch.delay(item['path'])
                else:
                    self.fetch(item['path'])

    @celery.task(filter=task_method)
    def fetch(self, path):
        fobj = self.client.get_file(path)

        path, save_loc = self.build_directories(path[1:])  # Remove beginning /

        self.chunked_save(fobj, path)
        store.push_file(path, save_loc)
