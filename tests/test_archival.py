import copy

import mock

import pytest

from archiver.datatypes import Container
from archiver.worker.tasks import archive, build_task_list
from archiver.worker.tasks.archivers import get_archiver

from utils import jsons


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


@pytest.fixture
def archive_mon(monkeypatch):
    mock_archive = mock.MagicMock()
    # mock_archive.side_effect = lambda c: archive(c)
    new_arc = copy.copy(build_task_list)
    mock_archive.side_effect = lambda c: new_arc(c)

    monkeypatch.setattr('archiver.worker.tasks.build_task_list', mock_archive)
    return mock_archive


def test_archive_service_not_implemented(container):
    service = container.services[0]
    service.service = 'FakeService'
    with pytest.raises(NotImplementedError) as err:
        get_archiver(service)
    assert err.type == NotImplementedError
    from archiver import settings


def test_archive_service_called(monkeypatch, container):
    mock_service_archive = mock.MagicMock()
    monkeypatch.setattr('archiver.worker.tasks.archive_service', mock_service_archive)

    assert len(container.services) == 1
    service = container.services[0]

    archive(container)

    mock_service_archive.assert_called_once()
    mock_service_archive.assert_called_once_with(service)


def test_archive_services_called(monkeypatch, container_many_services):
    mock_service_archive = mock.MagicMock()
    monkeypatch.setattr('archiver.worker.tasks.archive_service', mock_service_archive)

    assert len(container_many_services.services) > 1

    archive(container_many_services)

    calls = [mock.call(service) for service in container_many_services.services]
    mock_service_archive.assert_has_calls(calls, any_order=True)


@pytest.mark.usesfixtures('ignore_services')
def test_archive_child(monkeypatch, container_with_child, callback, ignore_services, archive_mon):
    assert len(container_with_child.children) == 1

    archive(container_with_child)

    assert callback.called
    assert archive_mon.called_with(container_with_child.children[0])


def test_archive_many_children(monkeypatch, container_with_children, callback, ignore_services, archive_mon):
    assert len(container_with_children.children) > 1

    archive(container_with_children)

    calls = collect_children_calls(container_with_children)
    archive_mon.assert_has_calls(calls, any_order=True)


def test_archive_nest_children(monkeypatch, container_nested_children, callback, ignore_services, archive_mon):
    assert len(container_nested_children.children) > 1

    archive(container_nested_children)

    assert callback.called

    calls = collect_children_calls(container_nested_children)
    assert len(calls) > 2

    archive_mon.assert_has_calls(calls, any_order=True)


def test_archive_children_services(monkeypatch, container_children_services,  callback, archive_mon, ignore_services):
    assert len(container_children_services.children) > 1

    archive(container_children_services)

    assert callback.called
    service_calls = collect_service_calls(container_children_services)
    container_calls = collect_children_calls(container_children_services)

    archive_mon.assert_has_calls(container_calls, any_order=True)
    ignore_services.assert_has_calls(service_calls, any_order=True)


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
