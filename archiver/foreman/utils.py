import json
try:
    import httplib as http  # Python 2
except ImportError:
    import http.client as http  # Python 3
from socket import error as SocketError

from tornado.web import HTTPError
from tornado.web import RequestHandler

from archiver.util import signing
from archiver.settings import URL_PREFIX
from archiver.worker.tasks import archive


#  Preprocessing would go here
def push_task(container):
    ret = {
        'response': {
            'id': container.id,
            'date': container.registered_on
        }
    }

    try:
        archive.delay(container)

        ret['status'] = http.CREATED
        ret['response']['status'] = 'STARTED'

    except SocketError as e:
        if e.errno in [54, 61]:
            # Connection reset by peer/ Connection refused
            # Genericly unable to connect to rabbit
            ret['response'].update({
                'status': 'ERROR',
                'reason': 'could not connect to rabbitmq'
            })
            ret['status'] = http.SERVICE_UNAVAILABLE
        else:
            raise
    except Exception:
        ret['response']['status'] =  'ERROR'
        ret['status'] = http.INTERNAL_SERVER_ERROR
    finally:
        return ret


class BaseAPIHandler(RequestHandler):
    URL = None

    @classmethod
    def as_route(cls):
        return (URL_PREFIX + cls.URL, cls, {}, cls.__name__)

    @property
    def json(self):
        try:
            return self._json
        except AttributeError:
            try:
                self._json = json.loads(self.request.body)
            except ValueError:
                raise HTTPError(http.BAD_REQUEST, reason='This route requires valid JSON.')
        return self._json

    def required_json(self, key):
        try:
            return self.json[key]
        except KeyError as e:
            raise HTTPError(http.BAD_GATEWAY, reason='This route requires a %s arugment' % e.value)

    # def json_is_signed(self, raise_if_false=True):
