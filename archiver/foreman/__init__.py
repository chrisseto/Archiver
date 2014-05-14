import logging

from celery import Celery

from flask import Flask

from archiver import settings

from views import rest

app = Flask(__name__)

logger = logging.getLogger(__name__)

celery = Celery()
celery.config_from_object(settings)


def start():
    ch = logging.StreamHandler()
    ch.setLevel(logging.INFO)
    ch.setFormatter(logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s'))
    logger.addHandler(ch)

    app.register_blueprint(rest)
    app.run(port=7000, debug=settings.DEBUG)
