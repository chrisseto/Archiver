from invoke import task, run


@task
def vagrant():
    run('cd vagrant && vagrant up')


@task
def build_worker():
    print 'TODO'


@task
def worker():
    run('celery -A registerer.celery worker -I registerer.tasks --loglevel=INFO')


@task
def docker_worker():
    run('celery -A registerer.celery worker -I registerer.tasks -b $SERVICE_PORT_5672_TCP_ADDR')


@task
def notebook():
    run('ipython notebook Tasking.ipynb')


@task
def flower():
    run('celery -A registerer.celery flower')


@task
def prepdocker():
    run('cp registerer/settings/local-celery.py vagrant/celeryworker/local.py')


@task
def clean():
    run('find . -name \*.pyc -delete')
