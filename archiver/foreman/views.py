import os

from flask import request, jsonify, Blueprint, redirect

from archiver.datatypes import Node
from archiver.backend.storage import get_file

from utils import push_task
from validation import ValidationError


rest = Blueprint('archiver', __name__)


@rest.route('/', methods=['POST', 'PUT'])
def begin_register():
    json = request.get_json(force=True)
    if json:
        node = Node.from_json(json)
        # Node should always be defined otherwise a
        # validation error will be raised by from_json
        if node:
            return push_task(node)
    raise ValidationError('no data')


@rest.route('/callback', methods=['POST', 'PUT'])
def callback():
    json = request.get_json(force=True)
    if json:
        print json
        return ''
    print "No data in callback"
    raise ValidationError('no data')


# Note the path may include id anyways....
@rest.route('/<id>/<path:name>')
def get_file_route(id, name):
    return redirect(get_file(os.path.join(id, name)))


@rest.route('/<id>/<path:directory>/list')
def get_dir_route(id, name):
    recurse = bool(request.parameters.get('recurse'))

    raise NotImplementedError()


@rest.route('/<id>/metadata')
def get_metadata_route(id):
    return redirect(get_file(os.path.join(id, 'metadata.json')))


@rest.errorhandler(ValidationError)
def handle_exception(error):
    response = jsonify(error.to_dict())
    response.status_code = error.status_code
    return response
