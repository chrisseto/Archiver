import json
import logging

from celery import chord, group

from archiver import celery
from archiver.backend import store
from archiver.worker.tasks import callbacks
from archiver.worker.tasks.archivers import get_archiver

logger = logging.getLogger(__name__)


@celery.task
def archive(container):
    header = [create_archive.si(container)]

    for service in container.services:
        header.append(archive_service.si(service))

    for child in container.children:
        header.append(archive.si(child))

    if container.is_child:
        c = group(header)
    else:
        c = chord(header, callbacks.archival_finish.s(container))

    c.delay()


@celery.task
def create_archive(container):
    logger.info('Begin archiving of "{}"'.format(container.title))

    container.make_dir()

    with open('{}metadata.json'.format(container.full_path), 'w+') as metadata:
        metadata.write(json.dumps(container.metadata()))

    store.push_directory(container.full_path, container.path)

    return container


@celery.task
def archive_service(service):
    #Lol one liners
    #WWSD
    get_archiver(service.service)(service).clone()
