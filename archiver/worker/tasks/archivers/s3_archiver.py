import logging

from boto.s3.connection import S3Connection, Key

from celery import chord

from archiver import celery
from archiver.backend import store

from base import ServiceArchiver


logger = logging.getLogger(__name__)


class S3Archiver(ServiceArchiver):
    ARCHIVES = 's3'
    RESOURCE = 'bucket'

    def __init__(self, service):
        self.connection = S3Connection(service['access_key'], service['secret_key'])
        self.bucket = self.connection.get_bucket(service['bucket'], validate=False)
        super(S3Archiver, self).__init__(service)

    def clone(self, versions=False):
        '''versions may be a truthy or falsey value or an integer specifing the number of versions desired
        '''
        header = self.build_header(versions)

        logger.info('{} files to archive from {}'.format(len(header), self.bucket.name))
        return chord(header, self.clone_done.s(self))

    def build_header(self, versions=None):
        header = []
        for key in self.bucket.list():
            if key.key[-1] == '/':
                continue

            if versions:
                header.extend(self.build_key_chord(key, versions))
            else:
                header.append(self.get_key.si(self, key))
        return header

    def build_key_chord(self, key, versions):
        header = [
            self.get_key.si(self, version)
            for version
            in self.bucket.get_all_versions(prefix=key.key)
            if isinstance(version, Key)
        ]
        return chord(header, self.key_done.s(self, key))

    @celery.task
    def get_key(self, key):
        fobj, path = self.get_temp_file()
        fobj.close()
        key.get_contents_to_filename(path)
        metadata = self.get_metadata(path, key.name)
        metadata['lastModified'] = self.to_epoch(key.last_modified)
        store.push_file(path, metadata['sha256'])
        store.push_json(metadata, '{}.json'.format(metadata['sha256']))
        return key, metadata

    @celery.task
    def key_done(rets, self, key):
        versions = {}
        ckey, current = rets[0]

        for vkey, metadata in rets:
            versions[vkey.version_id] = metadata
            if vkey.version_id == 'null' or metadata['lastModified'] > current['lastModified']:
                ckey, current = vkey, metadata

        return {
            'current': ckey.version_id,
            key.key: versions
        }

    @celery.task
    def clone_done(rets, self):
        files = []
        for ret in rets:
            if isinstance(ret, tuple):
                files.append(ret[1])
            else:
                files.append(ret)

        service = {
            'service': 's3',
            'resource': self.bucket.name,
            'files': files
        }
        store.push_json(service, '{}.s3.json'.format(self.cid))
        return service
