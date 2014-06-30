import json
import logging
import requests

from requests.exceptions import RequestException

from archiver import celery
from archiver.backend import store
from archiver.datatypes import Container
from archiver.settings import CALLBACK_ADDRESS

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
            store.push_manifest(failures, '%s.failures' % container.id)

        payload = {
            'status': 'success',
            'id': container.id,
            'failures': failures
        }

    else:
        payload = {
            'status': 'failed',
            'id': container.id,
            'reasons': errs
        }

    for address in CALLBACK_ADDRESS:
        try:
            requests.post(address, data=json.dumps(payload), headers=headers)
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
        }
    }

    store.push_manifest(manifest, container.id)
    store.push_directory_structure(manifest)
    return manifest


def parse_return_bundle(blob):
    bundle = []
    children = []

    for rvs in blob:
        if len(rvs) == 3:
            children.append(rvs[2])
            bundle.extend(zip(rvs[0], rvs[1]))
        else:
            bundle.append(rvs)

    manifest, failures = zip(*bundle)
    return manifest, [failure.to_json() for failure in sum(failures, [])], children
