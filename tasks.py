import os

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


@task
def purge():
    run('celery -A archiver.celery purge -f')


@task
def getpar2():
    cwd = os.getcwd()
    run('wget http://downloads.sourceforge.net/project/parchive/par2cmdline/0.4/par2cmdline-0.4.tar.gz')
    run('tar -xf par2cmdline-0.4.tar.gz')
    os.chdir('par2cmdline-0.4')
    run('wget http://sources.gentoo.org/cgi-bin/viewvc.cgi/gentoo-x86/app-arch/par2cmdline/files/par2cmdline-0.4-gcc4.patch?revision=1.1 -O reedsolomon.patch')
    run('patch -i reedsolomon.patch')
    run('./configure')
    run('make && make check && make install')
    os.chdir(cwd)
    run('rm -rf par2cmdline-0.4 par2cmdline-0.4.tar.gz')
