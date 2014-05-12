from flask import request, jsonify, Blueprint

from registerer import foreman
from registerer.datatypes import Node
from registerer.validation import ValidationError


rest = Blueprint('register', __name__)


@rest.route('/', methods=['POST', 'PUT'])
def begin_register():
    json = request.get_json(force=True)
    if json:
        node = Node.from_json(json)
        # Node should always be defined otherwise a
        # validation error will be raised by from_json
        if node:
            return foreman.push_task(node)
    raise ValidationError('no data')


@rest.route('/callback', methods=['POST', 'PUT'])
def callback():
    json = request.get_json(force=True)
    if json:
        print json
        return ''
    print "No data in callback"
    raise ValidationError('no data')


@rest.errorhandler(Exception)
def handle_exception(error):
    response = jsonify(error.to_dict())
    response.status_code = error.status_code
    return response
