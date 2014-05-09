import sys
import json
import logging

from git import Git

from registerer import celery
from registerer.backend.storage import push_directory
from registerer.tasks.callbacks import *
from registerer.tasks.exceptions import *

logger = logging.getLogger(__name__)


@celery.task
def create_registration(node):
    logger.info('Being registering of "{}"'.format(node.title))

    node.make_dir()

    with open('{}metadata.json'.format(node.path), 'w+') as metadata:
        metadata.write(json.dumps(node.metadata()))

    push_directory(node.title)

    return node


@celery.task
def register_addon(addon):
    cloner = _get_cloner(addon.addon)
    if cloner:
        cloner(addon)
    check_completion.delay(addon.parent.id)
    #Log error here


def _get_cloner(addon_name):
    self = sys.modules[__name__]
    return self.__dict__.get('_clone_{}'.format(addon_name))


def _clone_github(addon):
    #Note: Use git init and git pull
    # git clone will copy the key to .git/config
    clone_url = 'https://{token}@github.com/{user}/{repo}.git'
    try:
        token = addon['access_token']
        user = addon['user']
        repo = addon['repo']

        addon.make_dir(repo)
        url = clone_url.format(token=token, user=user, repo=repo)
        g = Git(addon.path(repo))
        g.init()
        g.execute(['git', 'pull', url])
        logger.info('Finished cloning github addon for {}')

        push_directory(addon.path(repo))

    except Exception:
        raise AddonCloningError('')
