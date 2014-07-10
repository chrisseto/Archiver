from StringIO import StringIO

import mock

import pytest

from archiver import settings
settings.BACKEND = 'debug'

from archiver.datatypes import Container
from archiver.worker.tasks.archivers import get_archiver
from archiver.worker.tasks.archivers.github_archiver import GithubArchiver

from utils import jsons


@pytest.fixture
def github_container():
    return Container.from_json(jsons.good)


@pytest.fixture
def github_service():
    return Container.from_json(jsons.good).services[0]


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


def test_github_called(monkeypatch, github_container, patch_callback):
    mock_git = mock.MagicMock()
    mock_git.return_value = None
    monkeypatch.setattr('archiver.worker.tasks.archivers.github_archiver.GithubArchiver.__init__', mock_git)
    monkeypatch.setattr('archiver.worker.tasks.archivers.github_archiver.GithubArchiver.clone', mock.Mock())
    assert get_archiver('github') == GithubArchiver


def test_sanitize(github_service):
    git_config = '{key}@github.com\n{key}othergitconfigstuff'.format(key=github_service['access_token'])
    mock_file = mock.MagicMock(spec=file, wraps=StringIO(git_config))
    assert github_service['access_token'] in mock_file.read()
    mock_file.seek(0)
    with mock.patch('archiver.worker.tasks.archivers.github_archiver.open', create=True) as mock_open:
        mock_open.return_value.__enter__.return_value = mock_file
        GithubArchiver(github_service).sanitize_config('')
    post_san = mock_file.read()
    assert post_san != git_config
    assert github_service['access_token'] not in post_san


def test_pulls_all_branches(monkeypatch):
    mock_git = mock.MagicMock()
    mock_git.branch.side_effect = mock_branches
    GithubArchiver.pull_all_branches(mock_git)
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

