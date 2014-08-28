import json
import base64
try:
    import httplib as http  # Python 2
except ImportError:
    import http.client as http  # Python 3
from socket import error as SocketError

from tornado.web import Finish
from tornado.web import HTTPError
from tornado.web import RequestHandler

from archiver import settings
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
        if settings.CELERY_SYNC:
            raise # If we're debugging we want to see all errors

        ret['response']['status'] =  'ERROR'
        ret['status'] = http.INTERNAL_SERVER_ERROR
    finally:
        return ret


class BaseAPIHandler(RequestHandler):
    URL = None

    @classmethod
    def as_route(cls):
        return (settings.URL_PREFIX + cls.URL, cls, {}, cls.__name__)

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

    def prepare(self):
        if settings.REQUIRE_AUTH:
            basic_auth = self.request.headers.get('Authorization', '').split(' ')

            try:
                api_key = base64.b64decode(basic_auth[1])
                api_key = api_key.split(':')[0]  # We dont care about the password
            except (TypeError, IndexError):
                self.set_status(401)
                self.set_header('WWW-Authenticate', 'Basic realm=%s' % 'Archiver')
                self._transforms = []
                raise Finish

            if api_key not in settings.API_KEYS:
                raise HTTPError(http.UNAUTHORIZED)

    def required_json(self, key):
        try:
            return self.json[key]
        except KeyError as e:
            raise HTTPError(http.BAD_GATEWAY, reason='This route requires a %s arugment' % e.value)
