from celery import Celery

from archiver import settings

if settings.SENTRY_DSN:
    from raven import Client
    from raven.contrib.celery import register_signal
    client = Client(settings.SENTRY_DSN)
    register_signal(client)


celery = Celery()
celery.config_from_object(settings)



def start():
    celery.worker_main(['prog_name', '--loglevel=INFO', '--autoscale=10,4'])
