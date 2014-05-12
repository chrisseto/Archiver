import logging

from celery import Celery

from flask import Flask

from registerer.settings import QUEUE_NAME, RABBITMQ_ADDRESS

app = Flask(__name__)
logger = logging.getLogger(__name__)
ch = logging.StreamHandler()
ch.setLevel(logging.INFO)
ch.setFormatter(logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s'))
logger.addHandler(ch)
celery = Celery(QUEUE_NAME, ampq=RABBITMQ_ADDRESS, backend='amqp')
