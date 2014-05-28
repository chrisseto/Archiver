import json
import logging

from celery import chord, group

from archiver import celery
from archiver.backend import store
from archiver.worker.tasks import callbacks
from archiver.worker.tasks.archivers import get_archiver

logger = logging.getLogger(__name__)


@celery.task
def archive(node):
    header = [create_archive.si(node)]

    for service in node.services:
        header.append(archive_service.si(service))

    for child in node.children:
        header.append(archive.si(child))

    if node.is_child:
        c = group(header)
    else:
        c = chord(header, callbacks.archival_finish.s(node))

    c.delay()


@celery.task
def create_archive(node):
    logger.info('Begin archiving of "{}"'.format(node.title))

    node.make_dir()

    with open('{}metadata.json'.format(node.full_path), 'w+') as metadata:
        metadata.write(json.dumps(node.metadata()))

    store.push_directory(node.full_path, node.path)

    return node


@celery.task
def archive_service(service):
    #Lol one liners
    #WWSD
    get_archiver(service.service)(service).clone()
