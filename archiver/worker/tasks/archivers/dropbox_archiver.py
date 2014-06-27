import sys
import logging

from celery import chord

from dateutil import parser

from dropbox.client import DropboxClient, ErrorResponse

from archiver import celery
from archiver.backend import store
from archiver.exceptions.archivers import DropboxArchiverError

from base import ServiceArchiver


logger = logging.getLogger(__name__)


class DropboxArchiver(ServiceArchiver):
    ARCHIVES = 'dropbox'

    def __init__(self, service):
        self.client = DropboxClient(service['access_token'])
        self.folder_name = service['folder']
        super(DropboxArchiver, self).__init__(service)

    def clone(self):
        header = self.build_header(self.folder_name, self.versions)
        logging.info('Archiving {} items from "{}"'.format(len(header), self.folder_name))
        return chord(header, clone_done.s(self))

    def build_header(self, folder, versions=None):
        header = []
        for item in self.client.metadata(folder)['contents']:
            if item['is_dir']:
                header.extend(self.build_header(item['path'], versions=versions))
            else:
                header.append(self.build_file_chord(item, versions=versions))
        return header

    def build_file_chord(self, item, versions=None):
        if not versions:
            return fetch.si(self, item['path'], rev=None)
        header = []
        for rev in self.client.revisions(item['path'], versions):
            header.append(fetch.si(self, item['path'], rev=rev['rev']))
        return chord(header, file_done.s(self, item['path']))


@celery.task(bind=True)
def fetch(self, dropbox, path, rev=None):
    try:
        fobj, metadata = dropbox.client.get_file_and_metadata(path, rev)
        tpath = dropbox.chunked_save(fobj)
        fobj.close()

    except ErrorResponse as e:

        if e.status == 461:
            logger.info('File {} is unavailable due to DMCA copyright reasons.')
            raise DropboxArchiverError('Failed to get file "{}", DMACA.'.format(path))

        logger.info('Failed to get file "{}"'.format(path))

        if e.headers.get('Retry-After'):
            logger.info('Hit Dropbox rate limit.')

        sys.exc_clear()

        raise self.retry(exc=DropboxArchiverError(
            'Failed to get file "{}".'.format(path)), countdown=e.headers.get('Retry-After', 60 * 3))

    lastmod = dropbox.to_epoch(parser.parse(metadata['modified']))
    metadata = dropbox.get_metadata(tpath, path)
    metadata['lastModified'] = lastmod
    store.push_file(tpath, metadata['sha256'])
    store.push_metadata(metadata, metadata['sha256'])
    metadata['path'] = metadata['path'].replace('{}/'.format(dropbox.folder_name), '')
    return metadata


@celery.task
def file_done(rets, dropbox, path):
    versions = {}
    current = rets[0]

    for item in rets:
        versions['rev'] = item
        if current['lastModified'] < item['lastModified']:
            current = item
    current['versions'] = versions
    return current


@celery.task
def clone_done(rets, dropbox):
    service = {
        'service': 'dropbox',
        'resource': dropbox.folder_name[1:],
        'files': rets
    }
    store.push_manifest(service, '{}.dropbox'.format(dropbox.cid))
    return service
