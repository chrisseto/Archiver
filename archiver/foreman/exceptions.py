import httplib as http

from flask import jsonify


class HTTPError(Exception):

    error_msgs = {
        http.BAD_REQUEST: {
            'message_short': 'Bad request',
            'message_long': 'Please ensure your data is correct and correctly formatted.',
        },
        http.UNAUTHORIZED: {
            'message_short': 'Unauthorized',
            'message_long': 'You do not have access this resource.',
        },
        http.FORBIDDEN: {
            'message_short': 'Forbidden',
            'message_long': 'You do not have permission to perform this action.',
        },
        http.NOT_FOUND: {
            'message_short': 'Resource not found',
            'message_long': 'The requested resource could not be found.',
        },
        http.GONE: {
            'message_short': 'Resource deleted',
            'message_long': 'The requested resource has been deleted.',
        },
        http.INTERNAL_SERVER_ERROR: {
            'message_short': 'Internal server error.',
            'message_short': 'An unhandle exception has occured.'
        }
    }

    def __init__(self, code, reason=''):

        super(HTTPError, self).__init__()

        self.code = code
        self.reason = reason

    def to_json(self):

        if self.code in self.error_msgs:
            data = {
                'message_short': self.error_msgs[self.code]['message_short'],
                'message_long': self.error_msgs[self.code]['message_long']
            }
        else:
            data['message_short'] = 'Unable to resolve'
            data['message_long'] = 'OSF was unable to resolve your request.  If this issue persists, please report it to <a href="mailto:support@osf.io">support@osf.io</a>.'

        data['code'] = self.code
        data['reason'] = self.reason

        return data

    def to_response(self):
        ret = jsonify(self.to_json())
        ret.status_code = self.code
        return ret


class ValidationError(HTTPError):
    def __init__(self, reason):
        super(ValidationError, self).__init__(400, reason=reason)
