from flask import request, jsonify, Blueprint

from registerer import foreman
from registerer.datatypes import Node
from registerer.validation import ValidationError


rest = Blueprint('register', __name__)


@rest.route('/', methods=['POST', 'PUT'])
def begin_register():
    if request.json:
        node = Node.from_json(request.json)
        # Node should always be defined otherwise a
        # validation error will be raised by from_json
        if node:
            return foreman.push_task(node)
    raise ValidationError('no data')


@rest.errorhandler(Exception)
def handle_exception(error):
    response = jsonify(error.to_dict())
    response.status_code = error.status_code
    return response
