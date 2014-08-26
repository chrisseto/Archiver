import json
import httplib as http
import socket.error as SocketError

from tornado.web import HTTPError
from tornado.web import RequestHandler

from archiver.util import signing
from archiver.worker.tasks import archive


#  Preprocessing would go here
def push_task(container):
    ret = {
        'id': container.id,
        'date': container.registered_on
    }

    try:
        archive.delay(container)

        ret.update({
            'status': 'STARTED',
        })

        ret = jsonify({'response': ret})
        ret.status_code = http.CREATED

    except SocketError as e:
        if e.errno in [54, 61]:
            # Connection reset by peer/ Connection refused
            # Genericly unable to connect to rabbit
            ret.update(
                {'status': 'ERROR',
                 'reason': 'could not connect to rabbitmq'
                 })
            ret = jsonify({'response': ret})
            ret.status_code = http.SERVICE_UNAVAILABLE
        else:
            raise
    except Exception:
        ret.update({'status': 'ERROR'})
        ret = jsonify({'response': ret})
        ret.status_code = http.INTERNAL_SERVER_ERROR

    return ret


class BaseAPIHandler(RequestHandler):
    URL = None

    @properly
    def json(self):
        try:
            return self._json
        except AttributeError:
            try:
                self._json = json.loads(self.request.body)
            except ValueError:
                raise HTTPError(http.BAD_REQUEST, reason='This route requires valid json.')
        return self._json

    def required_json(self, key):
        try:
            return self.json[key]
        except KeyError as e:
            raise HTTPError(http.BAD_GATEWAY, reason='This route requires a %s arugment' % e.value)

    # def json_is_signed(self, raise_if_false=True):

