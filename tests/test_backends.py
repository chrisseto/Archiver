import pytest

from archiver.backend import storage


@pytest.fixture(autouse=True)
def patch_s3(monkeypatch):
    monkeypatch.setattr('archiver.backend.storage.s3.S3Connection.get_bucket', lambda *_, **__: None)


def test_has_s3():
    backend = storage.get_storagebackend('s3')
    assert backend.__class__.__name__ == 'S3'


def test_has_debug():
    backend = storage.get_storagebackend('debug')
    assert backend.__class__.__name__ == 'Debug'


def test_returns_collection():
    backend = storage.get_storagebackends(['s3', 'debug'])
    assert backend.backends
    assert len(backend.backends) == 2
    assert backend.backends[0].__class__.__name__ == 'S3'
    assert backend.backends[1].__class__.__name__ == 'Debug'


def test_throws_on_empty():
    with pytest.raises(Exception) as e:
        storage.get_storagebackends([])
    assert e
    assert 'No backends specified' in str(e)


def test_redirects_with_one():
    backend = storage.get_storagebackends(['debug'])
    assert backend.__class__.__name__ == 'Debug'


def test_throws_bad_backend():
    with pytest.raises(NotImplementedError) as e:
        storage.get_storagebackend('Idontexist')
    assert e.type == NotImplementedError
    assert 'No backend for Idontexist' in str(e.value)
