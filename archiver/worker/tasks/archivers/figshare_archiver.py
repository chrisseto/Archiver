import os
import logging
import requests

from celery import chord

from requests_oauthlib import OAuth1Session

from celery.contrib.methods import task_method

from dateutil import parser

from archiver import celery
from archiver.backend import store
from archiver.settings import FIGSHARE_OAUTH_TOKENS
from archiver.exceptions.archivers import FigshareArchiverError, FigshareKeyError

from base import ServiceArchiver

logger = logging.getLogger(__name__)

class FigshareArchiver(ServiceArchiver):
    ARCHIVES = 'figshare'
    RESOURCE = ''
    API_URL = 'http://api.figshare.com/v1/'
    API_OAUTH_URL = API_URL + 'my_data/'

    def __init__(self, service):
        if None in FIGSHARE_OAUTH_TOKENS:
            raise FigshareKeyError('No OAuth tokens.')
        keys = [
            service['token_key'],
            service['token_secret'],
            FIGSHARE_OAUTH_TOKENS[0],
            FIGSHARE_OAUTH_TOKENS[1]
        ]
        self.client = self.create_oauth_session(*keys)
        self.fsid = service['id']
        super(FigshareArchiver, self).__init__(service)

    def clone(self):
        header = self.build_header()

        logger.info('{} files to archive from {}'.format(len(header), self.bucket.name))
        return chord(header, self.clone_done.s(self))

    def is_project(self):
        ret = self.client.get('{}projects'.format(self.API_OAUTH_URL))
        if not ret.ok:
            raise Exception()  # TODO
        for project in ret.json():
            if self.fsid == project['id']:
                return True
        return False

    #Assumes that self.fsid is an article
    def get_article_files(self):
        url = '{}articles/{}'.format(self.API_OAUTH_URL, self.fsid)
        ret = self.client.get(url)
        return ret.json()['items'][0]['files']

    #Assumes that self.fsid is an article
    def get_project_articles(self):
        url = '{}project/{}/articles'.format(self.API_OAUTH_URL, self.fsid)
        ret = self.client.get(url)
        return ret.json()

    @celery.task(filter=task_method)
    def download_file(self, filedict, aid):
        try:
            url = filedict['download_url']
            fobj, path = self.get_temp_file()
            fobj.close()
            stream = requests.get(url, stream=True)
            self.stream_file(stream, path)
            lastmod = self.to_epoch(path, aid)
            metadata = self.get_metadata(url, path)
            metadata['lastModified'] = lastmod
            store.push_file(url, metadata['sha256'])
            store.push_metadata(metadata, metadata['sha256'])
            return metadata
        except KeyError:
            pass

    @classmethod
    def create_oauth_session(cls, token_key, token_secret, client_key, client_secret):
        return OAuth1Session(client_key=client_key,
                             client_secret=client_secret,
                             resource_owner_key=token_key,
                             resource_owner_secret=token_secret)

    @classmethod
    def stream_download(cls, stream, save_loc):
        with open(save_loc, 'w+b') as save:
            for chunk in stream.iter_contents(chunk=1024):
                if chunk:
                    save.write(chunk)
                    save.flush()  # Needed?
        return True

    def build_header(self, id, versions=None):
        header = []
        if self.is_project():

            articles = self.get_project_articles()
            self.dirinfo['prefix'] += self.fsid
        else:
            articles = [{'id': self.fsid}]

        for article in articles:
            for afile in self.get_article_files():
                if afile['size'] > self.CUTOFF_SIZE:
                    header.append(self.build_header(id, versions=versions))
                else:
                    header.append(self.build_file_chord(afile, versions=versions))
        return header

    def build_file_chord(self, afile, versions=None):
        if not versions:
            return self.fetch.si(self, afile, rev=None)
        header = []
        for rev in self.client.revisions(afile, versions):
            header.append(self.fetch.si(self, afile, rev=rev['rev']))
        return chord(header, self.file_done.s(self, afile))

    @celery.task
    def download_file_done(rets, self, path):
        versions = {}
        current = rets[0]
        for item in rets:
            versions['rev'] = item
            if current['lastModified'] < item['lastModified']:
                current = item

        current['versions'] = versions
        return current

    @celery.task
    def clone_done(rets, self):
        service = {
            'service': 'figshare',
            'resource': self.id,
            'files': rets
        }
        store.push_manifest(service, '{}.figshare'.format(self.cid))
        return service
