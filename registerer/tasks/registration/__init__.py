import sys
import json
import logging

from registerer import celery
from registerer.backend.storage import push_directory
from registerer.tasks.callbacks import *
from registerer.tasks.exceptions import *

from . import github_clone, s3_clone, dropbox_clone

logger = logging.getLogger(__name__)


@celery.task
def create_registration(node):
    logger.info('Being registering of "{}"'.format(node.title))

    node.make_dir()

    with open('{}metadata.json'.format(node.full_path), 'w+') as metadata:
        metadata.write(json.dumps(node.metadata()))

    push_directory(node.full_path, node.path)

    return node


@celery.task
def register_addon(addon):
    self = sys.modules[__name__]
    try:
        cloner = self.__dict__.get('{}_clone'.format(addon.addon))
        cloner.clone(addon)
    except (KeyError, AttributeError):
        raise NotImplementedError()
