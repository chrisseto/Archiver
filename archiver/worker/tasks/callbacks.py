import json
import logging
import requests

from requests.exceptions import RequestException

from archiver import celery
from archiver.backend import store
from archiver.settings import CALLBACK_ADDRESS

logger = logging.getLogger(__name__)
headers = {'Content-type': 'application/json', 'Accept': 'text/plain'}


@celery.task
def archival_finish(rvs, container):
    errs = [error.message for error in rvs if isinstance(error, Exception)]

    if not errs:
        generate_manifest(rvs, container)

    logger.info('Registation finished for {}'.format(container.id))

    # Children dont get callbacks
    if container.is_child:
        return (rvs, container)

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


def generate_manifest(blob, container):
    manifest = {
        'metadata': container.metadata(),
        'services': {
            service['service']: service
            for service in blob
            if isinstance(service, dict)
        },
        'children': {
            child[1].id: generate_manifest(*child)
            for child in blob
            if isinstance(child, tuple)
        }
    }

    store.push_manifest(manifest, container.id)
    store.push_directory_structure(manifest)
    return manifest
