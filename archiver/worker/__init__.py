from celery import Celery

from archiver import settings

celery = Celery()
celery.config_from_object(settings)


def start():
    celery.worker_main(['prog_name', '--loglevel=INFO'])
