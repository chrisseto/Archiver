import logging

from celery import Celery

from flask import Flask

from registerer.settings import QUEUE_NAME, RABBITMQ_ADDRESS

app = Flask(__name__)
logger = logging.getLogger(__name__)
celery = Celery(QUEUE_NAME, ampq=RABBITMQ_ADDRESS, backend='amqp')
