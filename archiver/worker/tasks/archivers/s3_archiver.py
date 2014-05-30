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
        self.bucket = self.connection.get_bucket(service['bucket'], validate=False)  # TODO Should validate?
        super(S3Archiver, self).__init__(service)

    def clone(self, versions=False):
        '''versions may be a truthy or falsey value or an integer specifing the number of versions desired
        '''
        master_chord = []
        for key in self.bucket.list():
            if versions:

                header = [
                    self.get_key.si(self, version)
                    for version in
                    self.bucket.get_all_versions(prefix=key.key)
                    if isinstance(version, Key)
                    and key.key[-1] != '/'
                ]
                key_back = self.key_call_back.s(self, key)

                if isinstance(versions, int):
                    key_chord = chord(header[:versions], key_back)
                else:
                    key_chord = chord(header, key_back)
                master_chord.append(key_chord)

            else:
                master_chord.append(self.get_key.si(self, key))

        logger.info('{} files to archive from {}'.format(sum([len(_) for _ in master_chord]), self.bucket.name))
        return chord(master_chord, self.bucket_call_back.s(self))

    @celery.task
    def get_key(self, key):
        fobj, path = self.get_temp_file()
        fobj.close()
        key.get_contents_to_filename(path)
        metadata = self.get_metadata(path, key.name)
        store.push_file(path, metadata['sha256'])
        store.push_json(metadata, '{}.json'.format(metadata['sha256']))
        return key, metadata

    @celery.task
    def key_call_back(rets, self, key):
        versions = {
            vkey.version_id: metadata
            for vkey, metadata
            in rets
        }

        current = rets[0][0].version_id
        to_beat = rets[0][1]['lastModified']

        for k, m in rets:
            if k.version_id == 'null':
                current = 'null'
                break
            if m['lastModified'] < to_beat:
                to_beat = m['lastModified']
                current = k.version_id

        return {
            'current': current,
            key.key: versions
        }

    @celery.task
    def bucket_call_back(rets, self):
        service = {
            'service': 's3',
            'resource': self.bucket.name,
            'files': rets
        }
        store.push_json(service, '{}.s3.json'.format(self.cid))
        return service
