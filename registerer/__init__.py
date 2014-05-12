import logging

from celery import Celery

from flask import Flask

from registerer import settings

app = Flask(__name__)

logger = logging.getLogger(__name__)
ch = logging.StreamHandler()
ch.setLevel(logging.INFO)
ch.setFormatter(logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s'))
logger.addHandler(ch)

celery = Celery(settings.QUEUE_NAME, ampq=settings.RABBITMQ_ADDRESS, backend='amqp')
celery.config_from_object(settings)
