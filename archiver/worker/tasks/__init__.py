import logging

from celery import chord, group

from archiver import celery
from archiver.worker.tasks import callbacks
from archiver.worker.tasks.archivers import get_archiver

logger = logging.getLogger(__name__)


@celery.task
def archive(container):
    header = []

    for service in container.services:
        header.append(archive_service(service))

    for child in container.children:
        header.append(archive.si(child))

    if container.is_child:
        c = group(header)
    else:
        c = chord(header, callbacks.archival_finish.s(container))

    c.delay()


def archive_service(service):
    #Lol one liners
    #WWSD
    return get_archiver(service.service)(service).clone()
