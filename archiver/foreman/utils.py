import httplib as http
from socket import error as SocketError

from flask import jsonify

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
            ret.update(
                {'status': 'ERROR',
                 'reason': 'could not connect to rabbitmq'
                 })
            ret = jsonify({'response': ret})
            ret.status_code = http.INTERNAL_SERVER_ERROR
        else:
            raise
    except Exception:
        ret.update({'status': 'ERROR'})
        ret = jsonify({'response': ret})
        ret.status_code = http.INTERNAL_SERVER_ERROR

    return ret
