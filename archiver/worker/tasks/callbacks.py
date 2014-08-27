import json
import logging
import requests

from requests.exceptions import RequestException

from archiver import celery
from archiver import settings
from archiver.backend import store
from archiver.util.signing import sign
from archiver.settings import CALLBACK_ADDRESSES, IGNORE_CALLBACK_SSL

logger = logging.getLogger(__name__)
headers = {'Content-type': 'application/json', 'Accept': 'text/plain'}


@celery.task
def archival_finish(rvs, container):
    errs = [
        error.message
        for error in rvs
        if isinstance(error, Exception)
    ]

    if not errs:
        logger.info('Registation finished for {}'.format(container.id))

        manifests, failures, children = parse_return_bundle(rvs)

        manifest = generate_manifest(manifests, children, container)

        if failures:
            store.push_manifest([failure.to_json() for failure in failures], '%s.failures' % container.id)

        payload = {
            'status': 'success',
            'id': container.id,
            'failures': [failure.to_json() for failure in failures]
        }

    else:
        logger.error('Registation failed for {}'.format(container.id))

        payload = {
            'status': 'failed',
            'id': container.id,
            'reasons': errs
        }

    payload = sign(payload)

    for address in CALLBACK_ADDRESSES:
        try:
            requests.post(address, data=json.dumps(payload), headers=headers, verify=IGNORE_CALLBACK_SSL)
        except RequestException:
            logger.warning('Could not submit callback to %s' % address)

    if container.is_child:
        return (manifests, failures, (container, manifest))


def generate_manifest(blob, children, container):
    manifest = {
        'metadata': container.metadata(),
        'services': {
            service['service']: service
            for service in blob
        },
        'children': {
            child[0].id: child[1]
            for child in children
        },
        'storedAt': {
            'provider': settings.BACKEND,
            'container': settings.CONTAINER_NAME
        }
    }

    store.push_manifest(manifest, container.id)
    store.push_directory_structure(manifest)
    return manifest


def parse_return_bundle(blob):
    manifests, failures, children = [], [], []

    for rvs in blob:

        rvs = list(rvs)

        if isinstance(rvs[0], dict):
            rvs[0] = [rvs[0]]

        try:
            rvs[1] = sum(rvs[1], [])
        except TypeError:
            pass

        manifests.extend(rvs[0])
        failures.extend(rvs[1])

        try:
            children.append(rvs[2])
        except IndexError:
            pass

    return manifests, failures, children
