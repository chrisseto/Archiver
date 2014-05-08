"""
foreman.py
a module for passing tasks to celery workers
"""
import httplib as http
from flask import jsonify

from datetime import datetime

from tasks.management import register


#  TODO
#  Preprocessing would go here
#  Workflow planning
#   call partition task
#       partition just splits into more jobs
def push_task(node):
    ret = {
        'id': node.id,
        'date': datetime.now()
    }

    try:
        task = register.delay(node)

        ret.update({
            'status': 'SUCCESS',
            'tid': task.id
        })

        ret = jsonify({'response': ret})
        ret.status_code = http.CREATED

    except Exception:
        ret.update({'status': 'ERROR'})
        ret = jsonify({'response': ret})
        ret.status_code = http.INTERNAL_SERVER_ERROR

    return ret




