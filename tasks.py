from invoke import task, run


@task
def setup():
    run('chmod +x Foreman')
    run('chmod +x Worker')


@task
def vagrant():
    run('cd vagrant && vagrant up')


@task
def build_worker():
    print 'TODO'


@task
def foreman():
    run('./Foreman')


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
def prepdocker():
    run('cp archiver/settings/local-docker.py vagrant/celeryworker/local.py')


@task
def clean():
    run('find . -name \*.pyc -delete')
