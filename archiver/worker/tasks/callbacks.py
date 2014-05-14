import json
import logging
import requests

from archiver import celery
from archiver.settings import FOREMAN_ADDRESS


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
    requests.post('{}/callback'.format(FOREMAN_ADDRESS), data=json.dumps(payload), headers=headers)
    logger.info('Registation finished for {}'.format(node.id))
