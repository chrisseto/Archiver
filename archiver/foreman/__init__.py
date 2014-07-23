import sys
import logging

from celery import Celery

from flask import Flask

from archiver import settings
from archiver.exceptions import HTTPError

from views import rest

if settings.SENTRY_DSN:
    from raven.contrib.flask import Sentry
    sentry = Sentry(dsn=settings.SENTRY_DSN)

logger = logging.getLogger(__name__)

celery = Celery()
celery.config_from_object(settings)


def start(app):
    app.run(host='0.0.0.0', port=settings.PORT)


def config_logging():
    logging.basicConfig(
        stream=sys.stdout,
        level=logging.DEBUG,
        format='[%(asctime)s][%(levelname)s][%(name)s]: %(message)s',
        datefmt='%m-%d %H:%M'
    )


def build_app():
    app = Flask(__name__)

    if settings.SENTRY_DSN:
        sentry.init_app(app)

    app.config.from_object('archiver.settings')
    app.register_blueprint(rest)

    @app.errorhandler(HTTPError)
    def handle_exception(error):
        return error.to_response()

    return app
