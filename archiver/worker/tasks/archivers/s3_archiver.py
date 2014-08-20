import logging

from celery import chord

from boto.s3.connection import OrdinaryCallingFormat, S3Connection, Key

from archiver.backend import store
from archiver import celery, settings
from archiver.exceptions.archivers import FileTooLargeError, S3ArchiverError

from base import ServiceArchiver


logger = logging.getLogger(__name__)


class S3Archiver(ServiceArchiver):
    ARCHIVES = 's3'
    REQUIRED_KEYS = ['access_key', 'secret_key', 'bucket']

    def __init__(self, service):
        try:
            self.connection = S3Connection(service['access_key'], service['secret_key'])

            if service['bucket'] != service['bucket'].lower():
                self.connection.calling_format = OrdinaryCallingFormat()

        except KeyError as e:
            raise S3ArchiverError('Missing argument "%s"' % e.message)

        self.bucket = self.connection.get_bucket(service['bucket'], validate=False)

        super(S3Archiver, self).__init__(service)

    def clone(self):
        header = self.build_header()

        logger.info('{} files to archive from {}'.format(len(header), self.bucket.name))
        return chord(header, self.clone_done.s(self))

    def build_header(self):
        header = []
        for key in self.bucket.list():
            if key.key[-1] == '/':
                continue

            if self.versions:
                header.append(self.build_key_chord(key))
            else:
                header.append(self.get_key.si(self, key))
        return header

    def build_key_chord(self, key):
        header = [
            self.get_key.si(self, version)
            for version
            in self.bucket.get_all_versions(prefix=key.key)
            if isinstance(version, Key)
        ]
        return chord(header, self.key_done.s(self, key))

    @celery.task(throws=(FileTooLargeError, ))
    def get_key(self, key):
        if settings.MAX_FILE_SIZE and key.size > settings.MAX_FILE_SIZE:
            raise FileTooLargeError(key.key, 's3')

        fobj, path = self.get_temp_file()
        fobj.close()
        key.get_contents_to_filename(path)
        metadata = self.get_metadata(path, key.name)
        metadata['lastModified'] = self.to_epoch(key.last_modified)
        store.push_file(path, metadata['sha256'])
        store.push_metadata(metadata, metadata['sha256'])
        return key, metadata

    @celery.task
    def key_done(rets, self, key):
        ckey, current = rets[0]
        versions = {}

        for vkey, metadata in rets:
            versions[vkey.version_id] = metadata['sha256']
            if vkey.version_id == 'null' or metadata['lastModified'] > current['lastModified']:
                ckey, current = vkey, metadata
        current['versions'] = versions
        return current

    @celery.task
    def clone_done(rets, self):
        service = {
            'service': 's3',
            'resource': self.bucket.name,
            'files': [ret[1] for ret in rets if isinstance(ret, tuple)] +
            [ret for ret in rets if isinstance(ret, dict)]
        }
        store.push_manifest(service, '{}.s3'.format(self.cid))
        return (service, [])
