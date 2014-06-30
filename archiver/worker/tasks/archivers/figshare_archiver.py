import logging
import requests

from celery import chord

from requests_oauthlib import OAuth1Session

from archiver import celery
from archiver.backend import store
from archiver.settings import FIGSHARE_OAUTH_TOKENS
from archiver.exceptions.archivers import FigshareArchiverError, FigshareKeyError, UnfetchableFile

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
        self.fsid = str(service['id'])
        super(FigshareArchiver, self).__init__(service)

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

    def clone(self):
        header = self.build_header(self.fsid)
        logger.info('{} files to archive from {}'.format(len(header), self.fsid))
        return chord(header, clone_done.s(self))

    def build_header(self, id, versions=None):
        header = []
        if self.is_project():
            articles = self.get_project_articles()
        else:
            articles = [{'id': self.fsid}]

        for article in articles:
            for afile in self.get_article_files(aid=article['id']):
                header.append(download_file.si(self, afile, article['id']))
        return header

    def is_project(self):
        ret = self.client.get('{}projects'.format(self.API_OAUTH_URL))

        if not ret.ok:
            raise FigshareArchiverError('Could not connect to Figshare.')

        for project in ret.json():
            if self.fsid == str(project['id']):
                return True
        return False

    #Assumes that self.fsid is an article
    def get_article_files(self, aid=None):
        aid = aid or self.fsid
        url = '{}articles/{}'.format(self.API_OAUTH_URL, aid)

        ret = self.client.get(url)

        try:
            raise FigshareArchiverError(ret.json()['error'])
        except (KeyError, TypeError):
            return ret.json()['items'][0]['files']
        except:
            raise

    def get_project_articles(self, pid=None):
        pid = pid or self.fsid
        url = '{}projects/{}/articles'.format(self.API_OAUTH_URL, self.fsid)

        ret = self.client.get(url)

        try:
            raise FigshareArchiverError(ret.json()['error'])
        except (KeyError, TypeError):
            return ret.json()
        except:
            raise


@celery.task(throws=(UnfetchableFile, ))
def download_file(figshare, filedict, aid):
    try:
        url = filedict['download_url']
        fobj, path = figshare.get_temp_file()
        fobj.close()

        try:
            stream = requests.get(url, stream=True)
            figshare.stream_file(stream, path)
        except:
            raise download_file.retry()

        metadata = figshare.get_metadata(url, path)

        store.push_file(url, metadata['sha256'])
        store.push_metadata(metadata, metadata['sha256'])

        return metadata
    except KeyError:
        logger.info('Unable to download file %s, no download url given.' % filedict['name'])
        raise UnfetchableFile('No download link available', filedict['name'], 'figshare')


@celery.task
def clone_done(rets, figshare):
    service = {
        'service': 'figshare',
        'resource': figshare.fsid,
        'files': [ret for ret in rets if not isinstance(ret, UnfetchableFile)]
    }
    store.push_manifest(service, '{}.figshare'.format(figshare.cid))
    return (service, [ret for ret in rets if isinstance(ret, UnfetchableFile)])
