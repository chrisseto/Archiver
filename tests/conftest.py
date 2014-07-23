import mock

import pytest

from archiver import settings
settings.BACKEND = 'debug'
settings.CELERY_ALWAYS_EAGER = True
settings.CELERY_EAGER_PROPAGATES_EXCEPTIONS = True

from archiver.datatypes import Container

from utils import jsons, DebugArchiver


@pytest.fixture(autouse=True)
def push_file(monkeypatch):
    patched = mock.MagicMock()
    monkeypatch.setattr('archiver.backend.store.push_file', patched)
    return patched


@pytest.fixture(autouse=True)
def push_json(monkeypatch):
    patched = mock.MagicMock()
    monkeypatch.setattr('archiver.backend.store.push_json', patched)
    return patched


@pytest.fixture(autouse=True)
def upload_file(monkeypatch):
    patched = mock.MagicMock()
    monkeypatch.setattr('archiver.backend.store.upload_file', patched)
    return patched


@pytest.fixture(autouse=True)
def no_metadata(monkeypatch):
    fake_meta = {
        'lastModified': 5,
        'sha256': 'sha256',
        'path': 'path'
    }
    monkeypatch.setattr('archiver.worker.tasks.archivers.base.ServiceArchiver.get_metadata', lambda *_, **__: fake_meta)
    monkeypatch.setattr('archiver.worker.tasks.archivers.base.ServiceArchiver.to_epoch', lambda *_, **__: 8)


@pytest.fixture
def container(monkeypatch):
    return Container.from_json(jsons.container_with_dropbox)


@pytest.fixture
def callback(monkeypatch):
    patch = mock.MagicMock()
    monkeypatch.setattr('archiver.worker.tasks.callbacks.archival_finish.run', patch)
    return patch


@pytest.fixture
def ignore_services(monkeypatch):
    mock_archive = mock.MagicMock()
    mock_archive.return_value = DebugArchiver().clone()
    monkeypatch.setattr('archiver.worker.tasks.archive_service', mock_archive)
    return mock_archive
