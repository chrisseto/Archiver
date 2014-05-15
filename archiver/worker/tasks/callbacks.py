import json
import logging
import requests

from archiver import celery
from archiver.settings import FOREMAN_ADDRESS


logger = logging.getLogger(__name__)
headers = {'Content-type': 'application/json', 'Accept': 'text/plain'}


@celery.task
def archival_finish(rvs, node):
    errs = [error.message for error in rvs if isinstance(error, Exception)]

    payload = {
        'status': 'failed' if errs else 'success',
        'id': node.id,
        'reasons': errs
    }
    requests.post('{}/callback'.format(FOREMAN_ADDRESS), data=json.dumps(payload), headers=headers)
    logger.info('Registation finished for {}'.format(node.id))
