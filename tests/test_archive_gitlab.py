from StringIO import StringIO

import mock

import pytest

from archiver import settings
settings.BACKEND = 'debug'

from archiver.datatypes import Container
from archiver.worker.tasks.archivers import get_archiver
from archiver.worker.tasks.archivers.gitlab_archiver import GitlabArchiver

from utils import jsons


@pytest.fixture
def gitlab_container():
    return Container.from_json(jsons.good_with_gitlab)


@pytest.fixture
def gitlab_service():
    return Container.from_json(jsons.good_with_gitlab).services[0]


@pytest.fixture
def patch_callback(monkeypatch):
    mock_callback = mock.Mock()
    monkeypatch.setattr('archiver.worker.tasks.callbacks.archival_finish.run', mock_callback)
    return mock_callback


@pytest.fixture(autouse=True)
def celery_sync(monkeypatch):
    monkeypatch.setattr('archiver.settings.CELERY_ALWAYS_EAGER', True)
    monkeypatch.setattr('archiver.settings.CELERY_EAGER_PROPAGATES_EXCEPTIONS', True)


@pytest.fixture(autouse=True)
def dont_register(monkeypatch):
    monkeypatch.setattr('archiver.worker.tasks.archive', lambda container: container)


def test_gitlab_called(monkeypatch, gitlab_container, patch_callback):
    mock_git = mock.MagicMock()
    mock_git.return_value = None
    monkeypatch.setattr('archiver.worker.tasks.archivers.gitlab_archiver.GitlabArchiver.__init__', mock_git)
    monkeypatch.setattr('archiver.worker.tasks.archivers.gitlab_archiver.GitlabArchiver.clone', mock.Mock())
    assert get_archiver('gitlab') == GitlabArchiver


def test_sanitize(gitlab_service):
    git_config = 'http://50.116.57.122/user/{pid}/'.format(key=gitlab_service['pid'])
    mock_file = mock.MagicMock(spec=file, wraps=StringIO(git_config))
    assert gitlab_service['pid'] in mock_file.read()
    mock_file.seek(0)
    with mock.patch('archiver.worker.tasks.archivers.gitlab_archiver.open', create=True) as mock_open:
        mock_open.return_value.__enter__.return_value = mock_file
        GitlabArchiver(gitlab_service).sanitize_config('')
    post_san = mock_file.read()
    assert post_san != git_config
    assert gitlab_service['pid'] not in post_san


def test_pulls_all_branches(monkeypatch):
    mock_git = mock.MagicMock()
    mock_git.branch.side_effect = mock_branches
    GitlabArchiver.pull_all_branches(mock_git)
    kalls = [
        mock.call('--track', branch, branch)
        for branch in
        ['branchone', 'branch2']
    ]
    mock_git.branch.has_calls(kalls, any_order=True)
    assert mock_git.fetch.called
    assert mock_git.pull.called


def mock_branches(*args):
    if not args:
        return 'lastbranch'
    elif args[0] == '-a':
        return 'branchone\nbranch2\nlastbranch'
