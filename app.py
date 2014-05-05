import logging
import httplib as http

from flask import Flask, request, jsonify

from foreman import push_task
from datatypes import Node
from validation import ValidationError

app = Flask(__name__)
logger = logging.getLogger(__name__)


@app.route('/', methods=['POST', 'PUT'])
def begin_register():
    if request.json:
        node = Node.from_json(request.json)
        if node:
            push_task(node)
            return node.id, http.CREATED
    raise ValidationError('no data')


@app.errorhandler(Exception)
def handle_exception(error):
    response = jsonify(error.to_dict())
    response.status_code = error.status_code
    return response


if __name__ == '__main__':
    app.run(port=7000)
