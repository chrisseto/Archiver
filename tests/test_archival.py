import os
import json

import pytest

from archiver import celery
from archiver.datatypes import Node
from archiver.worker.tasks import archive
from archiver.worker.tasks.archival import create_archive, archive_addon

from utils import jsons


@pytest.fixture(autouse=True)
def ctrl_tempdir(monkeypatch, tmpdir):
    #Use py.test tmpdir
    monkeypatch.setattr('archiver.datatypes.node.Node.TEMP_DIR', str(tmpdir))
    #Dont push to S3
    monkeypatch.setattr('archiver.backend.storage.push_directory', lambda x: None)
    #Dont clean up after
    monkeypatch.setattr('archiver.backend.storage.clean_directory', lambda x: None)
    return tmpdir


@pytest.fixture
def node():
    return Node.from_json(jsons.good)


@pytest.fixture(autouse=True)
def celery_sync(monkeypatch):
    monkeypatch.setattr('archiver.settings.CELERY_ALWAYS_EAGER', True)
    monkeypatch.setattr('archiver.settings.CELERY_EAGER_PROPAGATES_EXCEPTIONS', True)


def test_create_registration(monkeypatch, ctrl_tempdir, node):
    create_archive(node)
    assert str(ctrl_tempdir) == node.TEMP_DIR
    assert len(os.listdir(node.full_path)) == 1
    assert os.path.exists(os.path.join(node.full_path, 'metadata.json'))
    with open(os.path.join(node.full_path, 'metadata.json'), 'r') as fobj:
        assert json.load(fobj) == node.metadata()


def test_archive_addon_not_implemented(node):
    addon = node.addons[0]
    addon.addon = 'FakeService'
    with pytest.raises(NotImplementedError) as err:
        archive_addon(addon)
    assert err.type == NotImplementedError


def test_archive_addon(node, monkeypatch, ctrl_tempdir):
    addon = node.addons[0]

    def git_mock(*args, **_):

        assert args[1][0] == 'git'
        if args[1][1] == 'pull':
            assert addon['access_token'] in args[1][2]
            assert addon['user'] in args[1][2]
            assert addon['repo'] in args[1][2]

    monkeypatch.setattr('archiver.worker.tasks.archival.github_clone.Git.execute', git_mock)
    archive_addon(addon)


def test_callback(monkeypatch, node):

    @celery.task
    def callback(*args, **kwargs):
        assert args[1] == node
        assert isinstance(args[0], list)

    monkeypatch.setattr('archiver.worker.tasks.callbacks.archival_finish', callback)
    node.addons = []
    node.children = []
    archive(node)
