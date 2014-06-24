import json
import logging
import requests

from requests.exceptions import RequestException

from archiver import celery
from archiver.backend import store
from archiver.settings import CALLBACK_ADDRESS
from archiver import settings

logger = logging.getLogger(__name__)
headers = {'Content-type': 'application/json', 'Accept': 'text/plain'}


@celery.task
def archival_finish(rvs, container):
    errs = [error.message for error in rvs if isinstance(error, Exception)]
    if not errs:
        meta = {
            'metadata': container.metadata(),
            'services': {service['service']: service for service in rvs if service}
        }
        store.push_manifest(meta, container.id)
        store.push_directory_structure(meta)
        if settings.OSF_URL:
            headers = {'Content-type': 'application/json', 'Accept': 'text/plain'}
            api_url = settings.API_URL + container.id + '/'
            url = settings.OSF_URL + container.id + '/'
            requests.post(api_url, {'archiver': 'finished', 'url':url}, headers=headers)
    payload = {
        'status': 'failed' if errs else 'success',
        'id': container.id,
        'reasons': errs
    }

    for address in CALLBACK_ADDRESS:
        try:
            requests.post(address, data=json.dumps(payload), headers=headers)
        except RequestException:
            logger.warning('Could not submit callback to %s' % address)

    logger.info('Registation finished for {}'.format(container.id))
