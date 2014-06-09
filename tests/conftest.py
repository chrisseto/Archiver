import mock

import pytest

from archiver.datatypes import Container

from utils import jsons


@pytest.fixture
def push_file(monkeypatch):
    patched = mock.MagicMock()
    monkeypatch.setattr('archiver.backend.store.push_file', patched)
    return patched


@pytest.fixture
def push_json(monkeypatch):
    patched = mock.MagicMock()
    monkeypatch.setattr('archiver.backend.store.push_json', patched)
    return patched


@pytest.fixture(autouse=True)
def no_metadata(monkeypatch):
    fake_meta = {
        'lastModified': 5,
        'sha256': 'sha256'
    }
    monkeypatch.setattr('archiver.worker.tasks.archivers.base.ServiceArchiver.get_metadata', lambda *_, **__: fake_meta)
    monkeypatch.setattr('archiver.worker.tasks.archivers.base.ServiceArchiver.to_epoch', lambda *_, **__: 8)


@pytest.fixture
def container(monkeypatch):
    return Container.from_json(jsons.container_with_dropbox)
