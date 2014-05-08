from invoke import task, run


@task
def vagrant():
    run('cd vagrant && vagrant up')


@task
def build_worker():
    print 'TODO'


@task
def worker():
    run('celery -A registerer.celery worker -I registerer.tasks')


@task
def docker_worker():
    run('celery -A registerer.celery worker -I registerer.tasks -b $SERVICE_PORT_5672_TCP_ADDR')
