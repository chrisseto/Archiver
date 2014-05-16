import os

from flask import request, jsonify, Blueprint, redirect

from archiver.backend import store
from archiver.datatypes import Node
from archiver.exceptions import ValidationError

from utils import push_task


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


@rest.route('/', methods=['GET'])
def list_projects():
    return jsonify({'projects': store.list_directory('')})


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
    return redirect(store.get_file(os.path.join(id, name)))


@rest.route('/<id>/<path:directory>/')
@rest.route('/<id>/', defaults={'directory': ''})
def get_dir_route(id, directory):
    recurse = request.args.get('recurse') is not None or request.args.get('r') is not None

    path = os.path.join(id, directory)
    ret = {
        'id': id,
        'recursive': recurse,
        'directory': store.list_directory(path, recurse=recurse)
    }
    return jsonify(ret)


@rest.route('/<id>/metadata')
def get_metadata_route(id):
    return redirect(store.get_file(os.path.join(id, 'metadata.json')))
