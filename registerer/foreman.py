"""
foreman.py
a module for passing tasks to celery workers
"""
from celery import Celery

from settings import QUEUE_NAME, RABBITMQ_ADDRESS

celery = Celery(QUEUE_NAME, ampq=RABBITMQ_ADDRESS, backend='amqp')


#  TODO
#  Preprocessing would go here
#  Workflow planning
#   call partition task
#       partition just splits into more jobs
def push_task(node):
    pass


def partition_task(node):
    pass


def queue_task(task, **kwargs):
    pass
