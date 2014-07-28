
import os
import logging
from tempfile import mkdtemp
from shutil import rmtree

from git import Git

from archiver import celery
from archiver.backend import store
from archiver.settings import GITLAB_IP

from base import ServiceArchiver

logger = logging.getLogger(__name__)


class GitlabArchiver(ServiceArchiver):
    ARCHIVES = 'gitlab'
    RESOURCE = 'repo'
    CLONE_TPL = 'http://{gitlabip}/{user}/{pid}.git'

    def __init__(self, service):
        self.pid = service['pid']
        self.user = service['user']
        self.url = self.CLONE_TPL.format(
            gitlabip=GITLAB_IP, pid=self.pid, user=self.user)
        super(GitlabArchiver, self).__init__(service)

    def clone(self):
        return clone_gitlab.si(self)

    def sanitize_config(self, path):
        git_path = os.path.join(path, '.git', 'config')
        with open(git_path, 'w+') as config:
            git_config = config.read()
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


def process_file(gitlab, path, filename):
    metadata = gitlab.get_metadata(path, filename)
    store.push_file(path, metadata['sha256'])
    store.push_metadata(metadata, metadata['sha256'])
    return metadata


@celery.task
def clone_gitlab(gitlab):
    path = mkdtemp()

    try:
        Git().clone(gitlab.url, path)
    except:
        raise clone_gitlab.retry()

    rets = []

    for root, dirs, files in os.walk(path):
        dirs[:] = [d for d in dirs if not d[0] == '.']
        rets.extend([
            process_file(gitlab, os.path.join(root, f),
                         os.path.join(root, f).replace('%s/' % path, ''))
            for f in files
        ])

    service = {
        'service': 'gitlab',
        'files': rets
    }
    store.push_manifest(service, '{}.gitlab'.format(gitlab.cid))
    rmtree(path)
    return (service, [])
>>>>>>> fec3982f02839628c323a93728deb6cf0e641c79
