import copy

import mock

import pytest

from celery import chord

from dropbox.client import ErrorResponse

from archiver import settings
settings.CELERY_ALWAYS_EAGER = True

from archiver import exceptions
from archiver.datatypes import Container
from archiver.worker.tasks.archivers import get_archiver
from archiver.worker.tasks.archivers import dropbox_archiver
from archiver.worker.tasks.archivers.dropbox_archiver import DropboxArchiver, fetch

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


@pytest.fixture
def mockbox(dropbox_service):
    MockDropBox.folder_name = dropbox_service['folder']
    return DropboxArchiver(dropbox_service)


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


def test_file_too_large(mockbox):
    settings.MAX_FILE_SIZE = 500
    path = mockbox.client.create_mock_item(size=600, append=True)['path']

    with pytest.raises(exceptions.archivers.FileTooLargeError) as e:
        fetch(mockbox, path)
    assert e.value.file == path
    settings.MAX_FILE_SIZE = None


def test_461(mockbox):
    path = mockbox.client.create_mock_item()['path']

    mockresp = mock.Mock()
    mockresp.status = 461  # DMCA Error

    mockbox.client.get_file_and_metadata = mock.MagicMock()
    mockbox.client.get_file_and_metadata.side_effect = ErrorResponse(mockresp, '')

    with pytest.raises(exceptions.archivers.UnfetchableFile) as e:
        fetch(mockbox, path)


def test_non_461(mockbox):
    path = mockbox.client.create_mock_item()['path']

    mockresp = mock.Mock()
    mockresp.status = 500  # Not DMCA Error

    mockbox.client.get_file_and_metadata = mock.MagicMock()
    mockbox.client.get_file_and_metadata.side_effect = ErrorResponse(mockresp, '')

    with pytest.raises(exceptions.archivers.DropboxArchiverError) as e:
        fetch(mockbox, path)


def test_retry(mockbox):
    otherfetch = copy.copy(dropbox_archiver.fetch)
    fetch = mock.MagicMock()
    fetch.side_effect = otherfetch

    path = mockbox.client.create_mock_item()['path']

    mockresp = mock.Mock()
    mockresp.status = 500  # Not DMCA Error

    mockbox.client.get_file_and_metadata = mock.MagicMock()
    mockbox.client.get_file_and_metadata.side_effect = ErrorResponse(mockresp, '')

    with pytest.raises(exceptions.archivers.DropboxArchiverError) as e:
        fetch(mockbox, path)

    assert fetch.mock_calls > 2


def test_everything_runs(monkeypatch, mockbox):
    monkeypatch.setattr(mockbox, 'chunked_save', lambda *_, **__: '')
    clone_chord = mockbox.clone()
    ret = clone_chord().get()
    assert isinstance(ret, tuple)
    assert isinstance(ret[0], dict)
    assert isinstance(ret[1], list)
