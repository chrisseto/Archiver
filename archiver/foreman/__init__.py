import sys
import logging

from celery import Celery

from tornado.ioloop import IOLoop
from tornado.web import Application

from archiver import settings
from archiver.foreman.views import collect_handlers


if settings.SENTRY_DSN:
    #TODO Integrate sentry
    from raven.contrib.tornado import AsyncSentryClient
    sentry = Sentry(dsn=settings.SENTRY_DSN)

logger = logging.getLogger(__name__)

celery = Celery()
celery.config_from_object(settings)


def config_logging():
    logging.basicConfig(
        stream=sys.stdout,
        level=logging.INFO,
        format='[%(asctime)s][%(levelname)s][%(name)s]: %(message)s',
        datefmt='%m-%d %H:%M'
    )


def start(port):
    application = Application(collect_handlers(),
        debug=settings.DEBUG)

    application.listen(port, xheaders=(not settings.DEBUG))
    IOLoop.instance().start()
