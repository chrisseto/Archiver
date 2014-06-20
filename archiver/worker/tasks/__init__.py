import logging

from celery import chord, group

from archiver import celery
from archiver.worker.tasks import callbacks
from archiver.exceptions.archivers import ArchiverError
from archiver.worker.tasks.archivers import get_archiver

logger = logging.getLogger(__name__)


@celery.task
def archive(container):
    header = []
    try:
        for service in container.services:
            logging.info('Found service {} for {}'.format(service.service, container.id))
            header.append(archive_service(service))
    except ArchiverError as e:
        pass  # TODO

    for child in container.children:
        logging.info('Found child {} for {}'.format(child.id, container.id))
        header.append(archive.si(child))

    if container.is_child:
        c = group(header)
    else:
        c = chord(header, callbacks.archival_finish.s(container))

    c.delay()


def archive_service(service):
    #Lol one liners
    #WWSD
    logger.info('Archiving service {} for {}'.format(service.service, service.parent.id))
    #Note .clone() should return an unstarted celery task
    return get_archiver(service.service)(service).clone()
