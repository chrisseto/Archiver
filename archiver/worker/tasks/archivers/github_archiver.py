import os
import logging
from tempfile import mkdtemp
from shutil import rmtree

from git import Git

from archiver import celery
from archiver.backend import store

from base import ServiceArchiver

logger = logging.getLogger(__name__)


class GithubArchiver(ServiceArchiver):
    ARCHIVES = 'github'
    RESOURCE = 'repo'
    CLONE_TPL = 'https://{token}@github.com/{user}/{repo}.git'

    def __init__(self, service):
        self.repo = service['repo']
        self.user = service['user']
        self.token = service['access_token']
        self.url = self.CLONE_TPL.format(token=self.token,
                                         user=self.user,
                                         repo=self.repo
                                         )
        super(GithubArchiver, self).__init__(service)

    def clone(self):
        return clone_github.si(self)

    def sanitize_config(self, path):
        git_path = os.path.join(path, '.git', 'config')
        with open(git_path, 'w+') as config:
            git_config = config.read()
            assert self.token in git_config
            git_config = git_config.replace('{}@'.format(self.token), '')
            git_config.replace(self.token, '')
            config.seek(0)
            config.write(git_config)
            # Just in case anything else is laying around
            config.truncate()

    @classmethod
    def pull_all_branches(cls, git):
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


def process_file(github, path, filename):
    metadata = github.get_metadata(path, filename)
    store.push_file(path, metadata['sha256'])
    store.push_metadata(metadata, metadata['sha256'])
    return metadata


@celery.task
def clone_github(github):
    path = mkdtemp()
    Git().clone(github.url, path)
    g = Git(path)
    github.pull_all_branches(g)
    #github.sanitize_config(path)

    rets = []

    for root, dirs, files in os.walk(path):
        dirs[:] = [d for d in dirs if not d[0] == '.']
        rets.extend([
            process_file(github, os.path.join(root, f), f)
            for f in files
        ])

    service = {
        'service': 'github',
        'resource': github.repo,
        'files': rets
    }
    store.push_manifest(service, '{}.github'.format(github.cid))
    rmtree(path)
    return service
