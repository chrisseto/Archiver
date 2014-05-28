from boto.s3.connection import S3Connection

from celery.contrib.methods import task_method

from archiver import celery
from archiver.backend import store

from base import ServiceArchiver


class S3Archiver(ServiceArchiver):
    ARCHIVES = 's3'
    RESOURCE = 'bucket'

    def __init__(self, service):
        self.connection = S3Connection(service['access_key'], service['secret_key'])
        self.bucket = self.connection.get_bucket(service['bucket'], validate=False)  # TODO Should validate?
        super(S3Archiver, self).__init__(service)

    def clone(self):
        for key in self.bucket.list():
            # Dont clone directory keys
            if key.key[-1] != '/':
                if key.size > self.CUTOFF_SIZE:
                    self.get_key.delay(key)
                else:
                    self.get_key(key)

    @celery.task(filter=task_method)
    def get_key(self, key):
        path, save_loc = self.build_directories(key.key)
        key.get_contents_to_filename(path)
        store.push_file(path, save_loc)
