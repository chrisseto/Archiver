import json
import logging
import requests

from archiver import celery
from archiver.settings import SERVER_ADDRESS


logger = logging.getLogger(__name__)
headers = {'Content-type': 'application/json', 'Accept': 'text/plain'}


@celery.task
def archival_finish(rvs, node):
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
