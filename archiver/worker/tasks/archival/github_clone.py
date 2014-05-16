import os
import logging

from git import Git

from archiver.backend import store

logger = logging.getLogger(__name__)

#Saves a bit of memory by defining up here
clone_url = 'https://{token}@github.com/{user}/{repo}.git'


#Note: git clone will copy the key to .git/config
def clone_github(addon):

    #Load up variables
    token = addon['access_token']
    user = addon['user']
    repo = addon['repo']

    #Make the folder structure
    addon.make_dir(repo)
    url = clone_url.format(token=token, user=user, repo=repo)
    Git().clone(url, addon.path(repo))

    #Create git object from the actual repo
    g = Git(addon.path(repo))

    pull_all_branches(g)
    #Make sure that the access token doesn't get archived
    sanatize_config(addon)

    logger.info('Finished cloning github addon for {}')

    store.push_directory(addon.full_path(repo), addon.path(repo))


def pull_all_branches(git):
    local_branches = [
        branch.replace('*', '').strip()
        for branch in git.branch().split('\n')
    ]

    branches = [
        (branch.strip().replace('remotes/origin/', ''), branch.strip())
        for branch in git.branch('-a').split('\n')
        if '*' not in branch and 'HEAD' not in branch
    ]

    [
        git.branch('--track', *branch)
        for branch in branches
        if branch[0] not in local_branches
    ]

    git.fetch('--all')
    git.pull('--all')


def sanatize_config(addon):
    with open(os.path.join(addon.path(addon['repo']), '.git', 'config'), 'r+') as config:
        git_config = config.read()
        config.write(git_config.replace('{}@'.format(addon['access_token']), ''))
        config.truncate()


#Export as clone
clone = clone_github
