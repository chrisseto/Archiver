import sys
import json
import logging

from archiver import celery
from archiver.backend import store
from archiver.worker.tasks.callbacks import *
from archiver.worker.tasks.exceptions import *

from . import github_clone, s3_clone, dropbox_clone, figshare_clone

logger = logging.getLogger(__name__)


@celery.task
def create_archive(node):
    logger.info('Begin archiving of "{}"'.format(node.title))

    node.make_dir()

    with open('{}metadata.json'.format(node.full_path), 'w+') as metadata:
        metadata.write(json.dumps(node.metadata()))

    store.push_directory(node.full_path, node.path)

    return node


@celery.task
def archive_addon(addon):
    self = sys.modules[__name__]
    try:
        cloner = self.__dict__.get('{}_clone'.format(addon.addon))
        if not cloner:
            raise NotImplementedError('No cloner for {}'.format(addon.addon))
    except (KeyError, AttributeError):
        raise NotImplementedError('No cloner for {}'.format(addon.addon))
    #Dont catch cloner exceptions
    cloner.clone(addon)

#TODO move cloners in to a cloners model inherit form BaseCloner
