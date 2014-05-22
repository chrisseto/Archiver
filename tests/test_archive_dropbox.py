import copy
import random
import string

import mock

import pytest

from archiver.datatypes import Node
from archiver.worker.tasks.archivers import get_archiver
from archiver.worker.tasks.archivers.dropbox_archiver import DropboxArchiver

from utils import jsons
from utils.clients import MockDropBox


@pytest.fixture(autouse=True)
def patch_client(monkeypatch):
    monkeypatch.setattr('archiver.worker.tasks.archivers.dropbox_archiver.DropboxClient', MockDropBox)


@pytest.fixture(autouse=True)
def dropbox_addon():
    return Node.from_json(jsons.node_with_dropbox).addons[0]


@pytest.fixture(autouse=True)
def dropbox_node():
    return Node.from_json(jsons.node_with_dropbox)


@pytest.fixture
def patch_push(monkeypatch):
    patched = mock.MagicMock()
    monkeypatch.setattr('archiver.worker.tasks.archivers.dropbox_archiver.store.push_file', patched)
    monkeypatch.setattr(DropboxArchiver, 'chunked_save', mock.MagicMock())

    return patched


def test_gets_called():
    assert get_archiver('dropbox') == DropboxArchiver


def test_recurses(monkeypatch, dropbox_addon):
    MockDropBox.folder_name = dropbox_addon['folder']
    archiver = DropboxArchiver(dropbox_addon)
    mock_fetch = mock.MagicMock()
    monkeypatch.setattr(archiver, 'fetch', mock_fetch)
    archiver.clone()
    assert mock_fetch.called
    kalls = archiver.client.collect_calls()
    mock_fetch.has_calls(kalls, any_order=True)


def test_pushes(monkeypatch, dropbox_addon, patch_push):
    MockDropBox.folder_name = dropbox_addon['folder']
    archiver = DropboxArchiver(dropbox_addon)
    archiver.clone()
    assert len(patch_push.mock_calls) == len(archiver.client.gets)
    assert len(patch_push.mock_calls) == len(archiver.client.collect_calls())
