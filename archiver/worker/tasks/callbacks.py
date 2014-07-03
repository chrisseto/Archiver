import hmac
import json
import logging
import hashlib
import requests
import time
import calendar

from requests.exceptions import RequestException

from archiver import celery
from archiver.backend import store
from archiver.settings import CALLBACK_ADDRESS, IGNORE_CALLBACK_SSL, HMAC_KEY

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
        payload = {
            'status': 'failed',
            'id': container.id,
            'reasons': errs
        }

    payload = stamp_and_sign(payload, key='id')

    for address in CALLBACK_ADDRESS:
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


def stamp_and_sign(package, key=None):
    time_stamp = calendar.timegm(time.gmtime())

    signature = hmac.new(
        key=HMAC_KEY,
        msg='{}{}'.format(
            time_stamp,
            package.get(key, ''),
        ),
        digestmod=hashlib.sha256,
    ).hexdigest()

    package.update({
        'timeStamp': time_stamp,
        'signature': signature
    })
    return package
