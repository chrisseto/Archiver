import os
import sys
import json
import logging

from git import Git

from registerer import celery
from registerer.backend.storage import push_directory
from registerer.tasks.exceptions import *

logger = logging.getLogger(__name__)


@celery.task
def create_registration(node):
    logger.info('Being registering of "{}"'.format(node.title))
    os.mkdir(node.title)

    with open('{}/metadata.json'.format(node.title), 'w+') as metadata:
        metadata.write(json.dumps(node['metadata']))

    push_directory(node.title)

    return node


@celery.task(serializer='json')
def register_addon(addon, data):
    cloner = _get_cloner(addon)
    if cloner:
        cloner(data)
    #Log error here


def _get_cloner(addon_name):
    self = sys.modules[__name__]
    return self.dict.get('_clone_{}'.format(addon_name))


def _clone_github(data):
    #Note: Use git init and git pull
    # git clone will copy the key to .git/config
    clone_url = 'https://{token}@github.com/{user}/{repo}.git'
    try:
        token = data['access_token']
        repo_name = 'github/{}'.format(data['repo'])
        user = data['user']
        url = clone_url(token=token, user=user, repo=repo)
        os.mkdir(repo_name)
        g = Git(repo_name)
        g.init()
        g.execute(['git', 'pull', url])
        logger.info('Finished cloning github addon for {}')
    except Exception:
        raise AddonCloningError('')
