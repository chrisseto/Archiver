import logging

from celery import chord

from archiver import celery
from archiver.worker.tasks import callbacks
from archiver.exceptions.archivers import ArchiverError
from archiver.worker.tasks.archivers import get_archiver

logger = logging.getLogger(__name__)


@celery.task
def archive(container):
    build_task_list(container).delay()


def archive_service(service):
    logger.info('Archiving service {} for {}'.format(service.service, service.parent.id))
    #WWSD
    #Lol one liners
    #Note .clone() should return an unstarted celery task
    return get_archiver(service.service)(service).clone()


def build_task_list(container):
    header = []
    try:
        for service in container.services:
            logging.info('Found service {} for {}'.format(service.service, container.id))
            header.append(archive_service(service))
    except ArchiverError as e:
        pass  # TODO

    for child in container.children:
        logging.info('Found child {} for {}'.format(child.id, container.id))
        header.append(build_task_list(child))

    return chord(header, callbacks.archival_finish.s(container))
