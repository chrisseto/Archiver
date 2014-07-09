import mock

import pytest

from celery import chord

from archiver import settings
settings.CELERY_ALWAYS_EAGER = True

from archiver.datatypes import Container
from archiver.worker.tasks.archivers import get_archiver
from archiver.worker.tasks.archivers import dropbox_archiver
from archiver.worker.tasks.archivers.dropbox_archiver import DropboxArchiver

from utils import jsons
from utils.clients import MockDropBox


@pytest.fixture(autouse=True)
def patch_client(monkeypatch):
    monkeypatch.setattr('archiver.worker.tasks.archivers.dropbox_archiver.DropboxClient', MockDropBox)


@pytest.fixture(autouse=True)
def dropbox_service():
    return Container.from_json(jsons.container_with_dropbox).services[0]


@pytest.fixture(autouse=True)
def dropbox_container():
    return Container.from_json(jsons.container_with_dropbox)


def test_gets_called():
    assert get_archiver('dropbox') == DropboxArchiver
    assert get_archiver('dropbox').ARCHIVES == 'dropbox'


def test_returns_chord(dropbox_service):
    MockDropBox.folder_name = dropbox_service['folder']
    archiver = get_archiver('dropbox')(dropbox_service)

    assert isinstance(archiver.clone(), chord)


def test_recurses(monkeypatch, dropbox_service):
    MockDropBox.folder_name = dropbox_service['folder']
    archiver = DropboxArchiver(dropbox_service)
    mock_fetch = mock.MagicMock()
    monkeypatch.setattr(dropbox_archiver.fetch, 'si', mock_fetch)
    archiver.clone()
    assert mock_fetch.called
    kalls = archiver.client.collect_calls()
    mock_fetch.has_calls(kalls, any_order=True)


def test_flat_list(monkeypatch, dropbox_service):
    MockDropBox.folder_name = dropbox_service['folder']
    archiver = DropboxArchiver(dropbox_service)
    mock_fetch = mock.MagicMock()
    monkeypatch.setattr(dropbox_archiver.fetch, 'si', mock_fetch)
    chord = archiver.clone()
    for task in chord.task:
        assert not isinstance(task, list)
