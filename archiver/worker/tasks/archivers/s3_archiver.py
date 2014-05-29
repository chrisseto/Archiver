from boto.s3.connection import S3Connection

from celery import chord
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
        master_chord = []
        for key in self.bucket.list():
            header = [
                self.get_key.si(version)
                for version in
                self.bucket.get_all_versions(prefix=key.key)
                if key.key[-1] != '/'
            ]
            master_chord.append(chord(header, self.key_call_back.s(key)))
        chord(master_chord, self.bucket_call_back.s()).delay()

    @celery.task(filter=task_method)
    def get_key(self, key):
        fobj, path = self.get_temp_file()
        fobj.close()
        key.get_contents_to_filename(path)
        metadata = self.get_metadata(path, key.name)
        store.push_file(path, metadata['sha256'])
        store.push_file(self.write_json(metadata), '{}.json'.format(metadata['sha256']))
        return key, metadata

    @celery.task(filter=task_method)
    def key_call_back(self, rets, key):
        versions = {
            key.version_id: metadata
            for key, metadata
            in rets
        }
        return {key.key: versions}

    @celery.task(filter=task_method)
    def bucket_call_back(self, rets):
        service = {
            'service': 's3',
            'resource': self.bucket.name,
            'files': rets
        }
        store.push_file(self.write_json(service), '{}.s3.json'.format(self.cid))
        return service

