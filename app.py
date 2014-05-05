import httplib as http

from flask import Flask, request, abort, jsonify

from validator import validate_project, ValidationError

app = Flask(__name__)


@app.route('/', methods=['POST', 'PUT'])
def begin_register():
    if request.json and validate_project(request.json):
        return 'Good job'
    raise ValidationError('no data')


@app.errorhandler(ValidationError)
def handle_validation_error(error):
    response = jsonify(error.to_dict())
    response.status_code = error.status_code
    return response


if __name__ == '__main__':
    app.run(port=7000)
