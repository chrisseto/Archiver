import os
import json
import logging
import httplib as http

from flask import request, jsonify, Blueprint

from archiver import settings
from archiver.util import signing
from archiver.backend import store
from archiver.datatypes import Container
from archiver.exceptions import ValidationError, HTTPError

from utils import push_task


logger = logging.getLogger(__name__)
rest = Blueprint('archiver', __name__)


@rest.route('/', methods=['POST', 'PUT'])
def begin_register():
    request_json = request.get_json(force=True)

    if settings.REQUIRE_SIGNED_SUBMITIONS and not signing.verify_submition(request_json):
        raise HTTPError(http.UNAUTHORIZED)

    if request_json:
        logger.info('New Archival request from %s' % request.environ['REMOTE_ADDR'])
        logger.info('===Raw json===')
        logger.info(json.dumps(request_json, indent=4, sort_keys=True))
        logger.info('===End json===')
        container = Container.from_json(request_json)
        # Container should always be defined otherwise a
        # validation error will be raised by from_json
        if container:
            if container.id in store.list_containers():
                raise ValidationError('Container ID already exists')
            return push_task(container)
    raise ValidationError('no data')


@rest.route('/', methods=['GET'])
def list_projects():
    return jsonify({'containers': store.list_containers()})


@rest.route('/callback', methods=['POST', 'PUT'])
def callback():
    callback_json = request.get_json(force=True)

    if not signing.verify_callback(callback_json):
        logger.warn('Incorrectly signed callback from %s' %
                    request.environ['REMOTE_ADDR'])
        raise HTTPError(http.UNAUTHORIZED)

    try:
        if callback_json['status'] == 'failed':
            logger.warn('Failed to archive {} because {}.'.format(
                callback_json['id'], ', '.join(callback_json['reasons'])))
        elif callback_json['status'] == 'success':
            logger.info('Successfully archived {} with failures {}. ({})'.format(
                callback_json['id'], ', '.join(callback_json['failures'], len(callback_json['failures']))))
        else:
            logger.warning('Unknown status from %s' % request.environ['REMOTE_ADDR'])

        logger.info('===Raw json===')
        logger.info(json.dumps(callback_json, indent=4, sort_keys=True))
        logger.info('===End json===')
    except:
        raise ValidationError('no data')


@rest.route('/<string(maxlength=60):cid>')
def get_metadata_route(cid):
    service = request.args.get('service')
    if service:
        return store.get_container_service(cid, service)
    return store.get_container(cid)


@rest.route('/<string(length=64):fid>')
def get_file_route(fid):
    try:
        request.args['metadata']
        return store.get_file(os.path.join(settings.METADATA_DIR, '{}.json'.format(fid)))
    except KeyError:
        name = request.args.get('name')
        return store.get_file(os.path.join(settings.FILES_DIR, fid), name=name)
