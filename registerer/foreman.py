"""
foreman.py
a module for passing tasks to celery workers
"""
import httplib as http
from flask import jsonify

from tasks.management import register


#  TODO
#  Preprocessing would go here
#  Workflow planning
#   call partition task
#       partition just splits into more jobs
def push_task(node):
    ret = {
        'id': node.id,
        'date': node.registered_on
    }

    try:
        register.delay(node)

        ret.update({
            'status': 'SUCCESS',
        })

        ret = jsonify({'response': ret})
        ret.status_code = http.CREATED

    except Exception:
        ret.update({'status': 'ERROR'})
        ret = jsonify({'response': ret})
        ret.status_code = http.INTERNAL_SERVER_ERROR

    return ret
