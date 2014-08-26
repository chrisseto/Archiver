from invoke import task, run

from archiver import settings
import archiver.foreman as foreman


@task
def server(port=None):
    port = port or settings.PORT
    print 'Starting server on port %i' % port
    foreman.config_logging()
    foreman.start(port=port)

@task
def vagrant():
    run('cd vagrant && vagrant up')

@task
def worker():
    run('./Worker')


@task
def docker_worker():
    run('celery -A archiver.celery worker -I archiver.worker.tasks -b $SERVICE_PORT_5672_TCP_ADDR')


@task
def notebook():
    run('ipython notebook Tasking.ipynb')


@task
def flower():
    run('celery -A archiver.celery flower')


@task
def clean():
    run('find . -name \*.pyc -delete')


@task
def purge():
    run('celery -A archiver.celery purge -f')
