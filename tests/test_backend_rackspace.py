import mock

import pytest

from tornado import web

from pyrax import exceptions

from archiver import settings
from archiver.backend import storage

from .utils import NULL_FUNC


@pytest.fixture(autouse=True)
def pyrax(monkeypatch):
    mock_pyrax = mock.Mock()
    mock_container = mock.Mock()
    mock_pyrax.cloudfiles.get_container.return_value = mock_container
    monkeypatch.setattr('archiver.backend.storage.rackspace.pyrax', mock_pyrax)
    return mock_container


@pytest.fixture(autouse=True)
def no_deleting(monkeypatch):
    monkeypatch.setattr('archiver.backend.storage.rackspace.os.remove', NULL_FUNC)


def test_has_rackspace():
    backend = storage.get_storagebackend('rackspace')
    assert backend.__class__.__name__ == 'RackSpace'


def test_setup_called_correctly(monkeypatch):
    pyrax = mock.Mock()
    monkeypatch.setattr('archiver.backend.storage.rackspace.pyrax', pyrax)

    backend = storage.get_storagebackend('rackspace')

    assert pyrax.settings.set.called
    assert pyrax.set_setting.called
    assert pyrax.set_credentials.called_once_with(settings.USERNAME, api_key=settings.PASSWORD)
    assert pyrax.cloudfiles.set_temp_url_key.called
    assert pyrax.cloudfiles.get_container.called_once_with(settings.CONTAINER_NAME)


def test_catches_noobject(pyrax):
    backend = storage.get_storagebackend('rackspace')
    pyrax.get_object.side_effect = exceptions.NoSuchObject

    assert backend.upload_file('', 'mycoolfile')


def test_catches_notfound(pyrax):
    backend = storage.get_storagebackend('rackspace')
    pyrax.get_object.side_effect = exceptions.NotFound('','')

    assert backend.upload_file('', 'mycoolfile')


def test_skips_upload_on_found(pyrax):
    backend = storage.get_storagebackend('rackspace')

    assert not backend.upload_file('', 'mycoolfile')
    assert not pyrax.upload_file.called


def test_get_file_catches_noobject(pyrax):
    backend = storage.get_storagebackend('rackspace')

    pyrax.get_object.side_effect = exceptions.NoSuchObject

    with pytest.raises(web.HTTPError) as e:
        backend.get_file('')

    assert e.value.status_code == 404

def test_get_file_catches_notfound(pyrax):
    backend = storage.get_storagebackend('rackspace')

    pyrax.get_object.side_effect = exceptions.NotFound('','')

    with pytest.raises(web.HTTPError) as e:
        backend.get_file('')

    assert e.value.status_code == 404
