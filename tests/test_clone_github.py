import os
import json
from StringIO import StringIO

import mock

import pytest

from archiver import settings
settings.BACKEND = 'debug'

from archiver.datatypes import Node
from archiver.worker.tasks import archive, archive_addon
from archiver.worker.tasks.archivers.github_archiver import GithubArchiver

from utils import jsons


@pytest.fixture
def github_node():
    return Node.from_json(jsons.good)


@pytest.fixture
def github_addon():
    return Node.from_json(jsons.good).addons[0]


@pytest.fixture
def patch_callback(monkeypatch):
    mock_callback = mock.Mock()
    monkeypatch.setattr('archiver.worker.tasks.callbacks.archival_finish.run', mock_callback)
    return mock_callback


@pytest.fixture(autouse=True)
def ctrl_tempdir(monkeypatch, tmpdir):
    #Use py.test tmpdir
    monkeypatch.setattr('archiver.datatypes.node.Node.TEMP_DIR', str(tmpdir))
    return tmpdir


@pytest.fixture(autouse=True)
def celery_sync(monkeypatch):
    monkeypatch.setattr('archiver.settings.CELERY_ALWAYS_EAGER', True)
    monkeypatch.setattr('archiver.settings.CELERY_EAGER_PROPAGATES_EXCEPTIONS', True)


@pytest.fixture(autouse=True)
def dont_register(monkeypatch):
    monkeypatch.setattr('archiver.worker.tasks.archive', lambda node: node)


def test_github_called(monkeypatch, github_node, patch_callback):
    mock_git = mock.MagicMock()
    mock_git.return_value = None
    monkeypatch.setattr('archiver.worker.tasks.archivers.github_archiver.GithubArchiver.__init__', mock_git)
    monkeypatch.setattr('archiver.worker.tasks.archivers.github_archiver.GithubArchiver.clone', mock.Mock())
    archive(github_node)
    assert patch_callback.called
    mock_git.assert_called_once_with(github_node.addons[0])


def test_folder_structure(monkeypatch, github_addon, ctrl_tempdir):
    monkeypatch.setattr(GithubArchiver, 'pull_all_branches', lambda *_: None)
    monkeypatch.setattr(GithubArchiver, 'sanitize_config', lambda *_: None)
    monkeypatch.setattr('archiver.worker.tasks.archivers.github_archiver.Git.execute', lambda *_, **__: None)
    GithubArchiver(github_addon).clone()
    assert os.path.exists(github_addon.full_path(github_addon['repo']))


def test_sanitize(github_addon):
    git_config = '{key}@github.com\n{key}othergitconfigstuff'.format(key=github_addon['access_token'])
    mock_file = mock.MagicMock(spec=file, wraps=StringIO(git_config))
    assert github_addon['access_token'] in mock_file.read()
    mock_file.seek(0)
    with mock.patch('__builtin__.open', create=True) as mock_open:
        mock_open.return_value = mock_file
        GithubArchiver(github_addon).sanitize_config('')
    assert not github_addon['access_token'] not in mock_file.read()
