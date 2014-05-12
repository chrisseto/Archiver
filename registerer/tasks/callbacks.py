import json
import logging
import requests

from registerer import celery
from registerer.settings import SERVER_ADDRESS


logger = logging.getLogger(__name__)
headers = {'Content-type': 'application/json', 'Accept': 'text/plain'}


@celery.task
def registration_failed(*args):
    print args
    if len(args) > 1:
        task = celery.AsyncResult(args[0])
        node = args[1]
        payload = {
            'status': 'failed',
            'message': str(task.result),
            'id': node.id
        }
        requests.post('{}/callback'.format(SERVER_ADDRESS), data=json.dumps(payload), headers=headers)
        logger.info('Registation failed for {}'.format(node.id))


@celery.task
def registration_finish(rvs, node):
    print rvs
    status = 'success'
    for ret in rvs:
        if isinstance(ret, Exception):
            status = 'failed'
            break

    payload = {
        'status': status,
        'message': 'successfully registered',
        'id': node.id
    }
    requests.post('{}/callback'.format(SERVER_ADDRESS), data=json.dumps(payload), headers=headers)
    logger.info('Registation finished for {}'.format(node.id))
