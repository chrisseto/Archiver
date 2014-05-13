import logging

from git import Git

from registerer.backend.storage import push_directory

logger = logging.getLogger(__name__)


def clone_github(addon):
    #Note: Use git init and git pull
    # git clone will copy the key to .git/config
    clone_url = 'https://{token}@github.com/{user}/{repo}.git'

    token = addon['access_token']
    user = addon['user']
    repo = addon['repo']

    addon.make_dir(repo)
    url = clone_url.format(token=token, user=user, repo=repo)
    g = Git(addon.full_path(repo))
    g.init()
    g.execute(['git', 'pull', url])
    logger.info('Finished cloning github addon for {}')

    push_directory(addon.full_path(repo), addon.path(repo))


#Export as clone
clone = clone_github
