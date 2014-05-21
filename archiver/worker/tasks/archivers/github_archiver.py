import os

from git import Git

from celery.contrib.methods import task_method

from archiver.backend import store

from base import ServiceArchiver


class GithubArchiver(ServiceArchiver):
    ARCHIVES = 'github'
    RESOURCE = 'repo'
    CLONE_TPL = 'https://{token}@github.com/{user}/{repo}.git'

    def __init__(self, addon):
        self.repo = addon['repo']
        self.user = addon['user']
        self.token = addon['access_token']
        self.url = self.CLONE_TPL.format(token=self.token,
                                         user=self.user,
                                         repo=self.repo
                                         )
        super(GithubArchiver, self).__init__(addon)

    def clone(self):
        path, save_loc = self.build_directories('')
        Git().clone(self.url, path)
        g = Git(path)
        self.pull_all_branches(g)
        self.sanitize_config(path)
        store.push_directory(path, save_loc)

    def sanitize_config(self, path):
        git_path = os.path.join(path, '.git', 'config')
        with open(git_path, 'r+') as config:
            git_config = config.read()
            config.write(git_config.replace('{}@'.format(self.token), ''))
            # Just in case anything else is laying around
            config.write(git_config.replace(self.token, ''))
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
