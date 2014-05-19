import os
import json
from StringIO import StringIO

import mock

import pytest

from archiver import settings
settings.BACKEND = 'debug'

from archiver.datatypes import Node
from archiver.worker.tasks import archive
from archiver.worker.tasks.archival import archive_addon, github_clone

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
    monkeypatch.setattr('archiver.worker.tasks.archival.github_clone.clone', mock_git)
    archive(github_node)
    assert patch_callback.called
    mock_git.assert_called_once_with(github_node.addons[0])


def test_folder_structure(monkeypatch, github_addon, ctrl_tempdir):
    monkeypatch.setattr(github_clone, 'pull_all_branches', lambda x: None)
    monkeypatch.setattr(github_clone, 'sanatize_config', lambda x: None)
    monkeypatch.setattr(github_clone.Git, 'execute', lambda *_, **__: None)
    github_clone.clone(github_addon)
    assert os.path.exists(github_addon.full_path(github_addon['repo']))


def test_sanatize(github_addon):
    git_config = '{key}@github.com\n{key}othergitconfigstuff'.format(key=github_addon['access_token'])
    mock_file = mock.MagicMock(spec=file, wraps=StringIO(git_config))
    with mock.patch('archiver.worker.tasks.archival.github_clone.open', create=True) as mock_open:
        mock_open.return_value = mock_file
        github_clone.sanatize_config(github_addon)
    assert not github_addon['access_token'] not in mock_file.read()
