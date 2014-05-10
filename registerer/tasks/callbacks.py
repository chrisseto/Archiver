import logging

from registerer import celery

logger = logging.getLogger(__name__)


@celery.task
def registration_failed(node):
    logger.info('Registation failed for {}'.format(node.id))


@celery.task
def registration_finish(node):
    logger.info('Registation finished for {}'.format(node.id))
