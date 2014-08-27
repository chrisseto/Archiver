import copy

import mock

import pytest

from archiver.datatypes import Container
from archiver.backend.storage import StorageBackEnd

@pytest.fixture
def backend():
    class CoolSubClass(StorageBackEnd):
        def __init__(self):
            self.upload_file = mock.Mock()
            self.list_directory = mock.Mock()
            self.get_file = mock.Mock()

        def get_file(self, *_, **__):pass
        def list_directory(self, *_, **__):pass
        def upload_file(self, *_, **__):pass

    return CoolSubClass()

def test_remove_func():
    repeatative = 'testthistestistestateststring'
    assert StorageBackEnd.remove(repeatative, 'test') == 'thisisastring'


def test_push_json(monkeypatch, backend):
    monkeypatch.setattr('archiver.backend.storage.base.os.fdopen', mock.Mock(return_value=mock.MagicMock()))
    monkeypatch.setattr('archiver.backend.storage.base.tempfile.mkstemp', mock.Mock(return_value=(2, 'path')))

    backend.push_json({}, 'name')

    assert backend.upload_file.called
    assert backend.upload_file.called_once_with('path', {}, 'name.json')


def test_push_manifest(backend):
    backend.push_json = mock.Mock()
    backend.push_manifest({}, 'mycoollmanifest')
    assert backend.push_json.called
    assert backend.push_json.called_once_with({}, 'mycoollmanifest.manifest')
