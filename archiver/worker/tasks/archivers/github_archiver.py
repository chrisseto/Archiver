import os
import logging

from git import Git

from celery import chord

from dateutil import parser

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
        header = self.build_header(self.url, self.versions)
        logging.info('Archiving {} items from "{}"'.format(len(header), self.url))
        return chord(header, self.clone_done.s(self))

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

    def build_header(self, url, versions=None):
        fobj, path = self.get_temp_file(url, versions)
        fobj.close()
        Git().clone(self.url, path)
        g = Git(path)
        self.pull_all_branches(g)
        self.sanitize_config(path)
        lastmod = self.to_epoch(self.url.last_modified)
        metadata = self.get_metadata(url, path)
        metadata['lastModified'] = lastmod
        store.push_file(url, metadata['sha256'])
        store.push_metadata(metadata, metadata['sha256'])
        return metadata


    def build_file_chord(self, url, versions=None):
        if not versions:
            return self.fetch.si(self, url, rev=None)
        header = []
        for rev in self.client.revisions(url, versions):
            header.append(self.fetch.si(self, url, rev=rev['rev']))
        return chord(header, self.file_done.s(self, url))

    @celery.task
    def file_done(rets, self, path):
        versions = {}
        current = rets[0]

        for item in rets:
            versions['rev'] = item
            if current['lastModified'] < item['lastModified']:
                current = item

        current['versions'] = versions
        return current

    @celery.task
    def clone_done(rets, self):
        service = {
            'service': 'github',
            'resource': self.repo_name,
            'files': rets
        }
        store.push_manifest(service, '{}.github'.format(self.cid))
        return service
