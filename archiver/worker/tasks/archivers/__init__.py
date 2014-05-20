from base import ServiceArchiver

from s3_archiver import S3Archiver
from github_archiver import GithubArchiver
from dropbox_archiver import DropboxArchiver
from figshare_archiver import FigshareArchiver


def get_archiver(serivce):
    for archiver in ServiceArchiver.__subclasses__():
        if archiver.ARCHIVES == serivce:
            return archiver
    raise NotImplementedError()
