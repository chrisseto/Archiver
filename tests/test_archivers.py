import pytest

from archiver.worker.tasks import archivers


def test_has_github():
    archiver = archivers.get_archiver('github')
    assert archiver.__name__ == 'GithubArchiver'


def test_has_s3():
    archiver = archivers.get_archiver('s3')
    assert archiver.__name__ == 'S3Archiver'


def test_has_dropbox():
    archiver = archivers.get_archiver('dropbox')
    assert archiver.__name__ == 'DropboxArchiver'


def test_has_figshare():
    archiver = archivers.get_archiver('figshare')
    assert archiver.__name__ == 'FigshareArchiver'


def test_throws():
    with pytest.raises(NotImplementedError) as err:
        archivers.get_archiver('notanarchiver')
    assert err.type == NotImplementedError
    assert str(err.value) == 'No archiver for notanarchiver'
