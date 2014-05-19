'''Figshare cloner
'''
import os
import json

import requests

from requests_oauthlib import OAuth1Session

from archiver import celery
from archiver.backend import store
from archiver.settings import FIGSHARE_OAUTH_TOKENS

from .utils import CUTOFF_SIZE, build_directories

API_URL = 'http://api.figshare.com/v1/'
API_OAUTH_URL = API_URL + 'my_data/'


def clone(addon):
    dirinfo = {
        'tempdir': addon.parent.TEMP_DIR,
        'prefix': addon.path(addon['id'])
    }

    keys = [
        addon['token_key'],
        addon['token_secret'],
        FIGSHARE_OAUTH_TOKENS[0],
        FIGSHARE_OAUTH_TOKENS[1]
    ]

    client = create_oauth_session(*keys)

    if is_project(addon['id'], client):
        articles = get_project_articles(addon['id'], client)
        dirinfo['prefix'] = addon.path('')
    else:
        articles = [{'id': addon['id']}]

    for article in articles:
        for afile in get_article_files(article['id'], client):
            if afile['size'] > CUTOFF_SIZE:
                download_file.delay(afile, article['id'], client, dirinfo)
            else:
                download_file(afile, article['id'], client, dirinfo)


def create_oauth_session(token_key, token_secret, client_key, client_secret):
    return OAuth1Session(client_key=client_key,
                         client_secret=client_secret,
                         resource_owner_key=token_key,
                         resource_owner_secret=token_secret)


def is_project(project_id, client):
    ret = client.get('{}projects'.format(API_OAUTH_URL))
    if not ret.ok:
        raise Exception()  # TODO
    for project in ret.json():
        if project_id == project['id']:
            return True
    return False


def get_article_files(article_id, client):
    ret = client.get('{}articles/{}'.format(API_OAUTH_URL, article_id))
    return ret.json()['items'][0]['files']


def get_project_articles(project_id, client):
    ret = client.get('{}project/{}/articles'.format(API_OAUTH_URL, project_id))
    return ret.json()


@celery.task
def download_file(filedict, article_id, client, dirinfo):
    try:
        url = filedict['download_url']
        prepath = os.path.join(article_id, filedict['name'])
        path, save_loc = build_directories(dirinfo, prepath)
        stream = requests.get(url, stream=True)
        stream_file(stream, save_loc)
        store.push_file(path, save_loc)
    except KeyError:
        pass


def stream_file(stream, save_loc):
    with open(save_loc, 'w+b') as save:
        for chunk in stream.iter_contents(chunk=1024):
            if chunk:
                save.write(chunk)
                save.flush()  # Needed?
    return True
