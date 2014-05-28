import os
import json

import mock

import pytest

from archiver import settings
settings.BACKEND = 'debug'

from archiver.datatypes import Container
from archiver.worker.tasks import archive, create_archive, archive_service

from utils import jsons


@pytest.fixture(autouse=True)
def ctrl_tempdir(monkeypatch, tmpdir):
    #Use py.test tmpdir
    monkeypatch.setattr('archiver.datatypes.container.Container.TEMP_DIR', str(tmpdir))
    return tmpdir


@pytest.fixture
def patch_callback(monkeypatch):
    mock_callback = mock.Mock()
    monkeypatch.setattr('archiver.worker.tasks.callbacks.archival_finish.run', mock_callback)
    return mock_callback


@pytest.fixture
def container():
    return Container.from_json(jsons.good)


@pytest.fixture
def container_with_child():
    return Container.from_json(jsons.good_with_children)


@pytest.fixture
def container_with_children():
    return Container.from_json(jsons.good_multi_children)


@pytest.fixture
def container_nested_children():
    return Container.from_json(jsons.good_nested_children)


@pytest.fixture
def container_many_services():
    return Container.from_json(jsons.good_multi_service)


@pytest.fixture
def container_children_services():
    return Container.from_json(jsons.good_children_service)


@pytest.fixture(autouse=True)
def celery_sync(monkeypatch):
    monkeypatch.setattr('archiver.settings.CELERY_ALWAYS_EAGER', True)
    monkeypatch.setattr('archiver.settings.CELERY_EAGER_PROPAGATES_EXCEPTIONS', True)


def test_create_registration(monkeypatch, ctrl_tempdir, container):
    create_archive(container)
    assert str(ctrl_tempdir) == container.TEMP_DIR
    assert len(os.listdir(container.full_path)) == 1
    assert os.path.exists(os.path.join(container.full_path, 'metadata.json'))
    with open(os.path.join(container.full_path, 'metadata.json'), 'r') as fobj:
        assert json.load(fobj) == container.metadata()


def test_archive_service_not_implemented(container):
    service = container.services[0]
    service.service = 'FakeService'
    with pytest.raises(NotImplementedError) as err:
        archive_service(service)
    assert err.type == NotImplementedError


def test_archive_service_called(monkeypatch, container, ctrl_tempdir, patch_callback):
    mock_service_archive = mock.MagicMock()
    monkeypatch.setattr('archiver.worker.tasks.archive_service.run', mock_service_archive)

    assert len(container.services) == 1
    service = container.services[0]
    assert service.service == 'github'

    archive(container)

    assert patch_callback.called
    mock_service_archive.assert_called_once()
    mock_service_archive.assert_called_once_with(service)


def test_archive_services_called(monkeypatch, container_many_services, ctrl_tempdir, patch_callback):
    mock_service_archive = mock.MagicMock()
    monkeypatch.setattr('archiver.worker.tasks.archive_service.run', mock_service_archive)

    assert len(container_many_services.services) > 1

    archive(container_many_services)

    assert patch_callback.called

    calls = [mock.call(service) for service in container_many_services.services]
    mock_service_archive.assert_has_calls(calls, any_order=True)


def test_archive_child(monkeypatch, container_with_child, ctrl_tempdir, patch_callback):
    mock_child_archive = mock.MagicMock()
    monkeypatch.setattr('archiver.worker.tasks.create_archive.run', mock_child_archive)
    #Dont clone services
    monkeypatch.setattr('archiver.worker.tasks.archive_service.run', mock.MagicMock())

    assert len(container_with_child.children) == 1
    child = container_with_child.children[0]

    archive(container_with_child)

    assert patch_callback.called
    assert mock_child_archive.call_count == 2
    mock_child_archive.assert_has_calls([mock.call(child), mock.call(container_with_child)], any_order=True)


def test_archive_many_children(monkeypatch, container_with_children, ctrl_tempdir, patch_callback):
    mock_child_archive = mock.MagicMock()
    monkeypatch.setattr('archiver.worker.tasks.create_archive.run', mock_child_archive)
    #Dont clone services
    monkeypatch.setattr('archiver.worker.tasks.archive_service.run', lambda *_, **__: None)

    assert len(container_with_children.children) > 1

    archive(container_with_children)

    assert patch_callback.called

    calls = collect_children_calls(container_with_children)
    mock_child_archive.assert_has_calls(calls, any_order=True)
    assert len(calls) == len(mock_child_archive.mock_calls)


def test_archive_nest_children(monkeypatch, container_nested_children, ctrl_tempdir, patch_callback):
    mock_child_archive = mock.MagicMock()
    monkeypatch.setattr('archiver.worker.tasks.create_archive.run', mock_child_archive)
    #Dont clone services
    monkeypatch.setattr('archiver.worker.tasks.archive_service.run', lambda *_, **__: None)

    assert len(container_nested_children.children) > 1

    archive(container_nested_children)

    assert patch_callback.called

    calls = collect_children_calls(container_nested_children)
    assert len(calls) > 2

    mock_child_archive.assert_has_calls(calls, any_order=True)
    assert len(calls) == len(mock_child_archive.mock_calls)


def test_archive_children_services(monkeypatch, container_children_services, ctrl_tempdir, patch_callback):
    mock_child_archive = mock.MagicMock()
    mock_service_archive = mock.MagicMock()
    monkeypatch.setattr('archiver.worker.tasks.create_archive.run', mock_child_archive)
    monkeypatch.setattr('archiver.worker.tasks.archive_service.run', mock_service_archive)

    assert len(container_children_services.children) > 1

    archive(container_children_services)

    assert patch_callback.called
    service_calls = collect_service_calls(container_children_services)
    container_calls = collect_children_calls(container_children_services)

    assert len(container_calls) == len(mock_child_archive.mock_calls)
    mock_child_archive.assert_has_calls(container_calls, any_order=True)

    assert len(service_calls) == len(mock_service_archive.mock_calls)
    mock_service_archive.assert_has_calls(service_calls, any_order=True)


def collect_service_calls(container):
    service_calls = [mock.call(service) for service in container.services]
    for child in container.children:
        service_calls.extend(collect_service_calls(child))
    return service_calls


def collect_children_calls(container):
    kid_calls = [mock.call(container)]
    for child in container.children:
        # kid_calls.append(mock.call(child))
        kid_calls.extend(collect_children_calls(child))
    return kid_calls
