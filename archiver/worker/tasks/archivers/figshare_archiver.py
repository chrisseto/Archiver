import os

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
        if self.is_project():
            articles = self.get_project_articles()
            self.dirinfo['prefix'] += self.fsid
        else:
            articles = [{'id': self.fsid}]

        for article in articles:
            for afile in self.get_article_files():
                if afile['size'] > self.CUTOFF_SIZE:
                    self.download_file.delay(afile, article['id'])
                else:
                    self.download_file(afile, article['id'])

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
            prepath = os.path.join(aid, filedict['name'])
            path, save_loc = self.build_directories(prepath)
            stream = requests.get(url, stream=True)
            self.stream_file(stream, save_loc)
            store.push_file(path, save_loc)
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
        for item in self.client.metadata(id)['contents']:
            if item['is_dir']:
                header.append(self.build_header(item['path'], versions=versions))
            else:
                header.append(self.build_file_chord(item, versions=versions))
        return header

    def build_file_chord(self, item, versions=None):
        if not versions:
            return self.fetch.si(self, item['path'], rev=None)
        header = []
        for rev in self.client.revisions(item['path'], versions):
            header.append(self.fetch.si(self, item['path'], rev=rev['rev']))
        return chord(header, self.file_done.s(self, item['path']))

    @celery.task
    def fetch(self, path, rev=None):
        fobj, metadata = self.client.get_file_and_metadata(path, rev)
        tpath = self.chunked_save(fobj)
        fobj.close()
        lastmod = self.to_epoch(parser.parse(metadata['modified']))
        metadata = self.get_metadata(tpath, path)
        metadata['lastModified'] = lastmod
        store.push_file(tpath, metadata['sha256'])
        store.push_metadata(metadata, metadata['sha256'])
        return metadata

    @celery.task
    def file_done(rets, self, path):
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
