#!/usr/bin/env python
# -*- coding: utf-8 -*-
from invoke import run, task


@task
def provision(inventory='hosts', user='vagrant', sudo=True, verbose=False, extra='', key='~/.vagrant.d/insecure_private_key'):
    """Run the site.yml playbook given an inventory file and a user. Defaults
    to provisioning the vagrant box.
    """
    play(playbook='site.yml',
         inventory=inventory,
         user=user,
         sudo=sudo,
         verbose=verbose, extra=extra, key=key)


@task
def play(playbook, inventory='hosts', user='vagrant', sudo=True, verbose=False, extra='', key=''):
    """Run a playbook. Defaults to using the vagrant inventory and vagrant user."""
    print('[invoke] Playing {0!r} on {1!r} with user {2!r}...'.format(
        playbook, inventory, user))
    cmd = 'ansible-playbook {playbook} -i {inventory} -u {user}'.format(**locals())
    if sudo:
        cmd += ' -s'
    if verbose:
        cmd += ' -vvvv'
    if key:
        cmd += ' --private-key=%s' % key
    if extra:
        cmd += ' -e {0!r}'.format(extra)
    print('[invoke] {0!r}'.format(cmd))
    run(cmd, pty=True)


@task
def vagrant_recycle():
    run('vagrant destroy -f')
    run('vagrant up')
    provision()
