from invoke import task, run


@task
def vagrant():
    run('cd vagrant && vagrant up')


@task
def build_worker():
    print 'TODO'
