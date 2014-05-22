import logging

from celery import Celery

from flask import Flask

from archiver import settings
from archiver.exceptions import HTTPError

from views import rest

logger = logging.getLogger(__name__)

celery = Celery()
celery.config_from_object(settings)


def start():
    ch = logging.StreamHandler()
    ch.setLevel(logging.INFO)
    ch.setFormatter(logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s'))
    logger.addHandler(ch)

    app = build_app()
    app.run()


def build_app():
    app = Flask(__name__)
    app.config.from_object('archiver.settings')
    app.register_blueprint(rest)

    @app.errorhandler(HTTPError)
    def handle_exception(error):
        return error.to_response()

    return app
