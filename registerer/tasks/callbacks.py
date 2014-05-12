import json
import logging
import requests

from registerer import celery
from registerer.settings import SERVER_ADDRESS


logger = logging.getLogger(__name__)
headers = {'Content-type': 'application/json', 'Accept': 'text/plain'}


@celery.task
def registration_failed(node, exc, task_id, args, kwargs, einfo):
    payload = {
        'status': 'failed',
        'message': str(exc),
        'id': node.id
    }
    requests.post(SERVER_ADDRESS, data=json.dumps(payload), headers=headers)
    logger.info('Registation failed for {}'.format(node.id))


@celery.task
def registration_finish(node):
    payload = {
        'status': 'finished',
        'message': 'successfully registered',
        'id': node.id
    }
    requests.post(SERVER_ADDRESS, data=json.dumps(payload), headers=headers)
    logger.info('Registation finished for {}'.format(node.id))
