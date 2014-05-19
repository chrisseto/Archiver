import os
import json

import mock

import pytest

from celery.app.task import EagerResult

from archiver import settings
settings.BACKEND = 'debug'

from archiver.datatypes import Node
from archiver.worker.tasks import archive
from archiver.worker.tasks.archival import create_archive, archive_addon

from utils import jsons


@pytest.fixture(autouse=True)
def ctrl_tempdir(monkeypatch, tmpdir):
    #Use py.test tmpdir
    monkeypatch.setattr('archiver.datatypes.node.Node.TEMP_DIR', str(tmpdir))
    return tmpdir


@pytest.fixture
def patch_callback(monkeypatch):
    mock_callback = mock.Mock()
    monkeypatch.setattr('archiver.worker.tasks.callbacks.archival_finish.run', mock_callback)
    return mock_callback


@pytest.fixture
def node():
    return Node.from_json(jsons.good)


@pytest.fixture
def node_with_child():
    return Node.from_json(jsons.good_with_children)


@pytest.fixture
def node_with_children():
    return Node.from_json(jsons.good_multi_children)


@pytest.fixture
def node_nested_children():
    return Node.from_json(jsons.good_nested_children)


@pytest.fixture
def node_many_addons():
    return Node.from_json(jsons.good_multi_addon)


@pytest.fixture(autouse=True)
def celery_sync(monkeypatch):
    monkeypatch.setattr('archiver.settings.CELERY_ALWAYS_EAGER', True)
    monkeypatch.setattr('archiver.settings.CELERY_EAGER_PROPAGATES_EXCEPTIONS', True)


def test_create_registration(monkeypatch, ctrl_tempdir, node):
    create_archive(node)
    assert str(ctrl_tempdir) == node.TEMP_DIR
    assert len(os.listdir(node.full_path)) == 1
    assert os.path.exists(os.path.join(node.full_path, 'metadata.json'))
    with open(os.path.join(node.full_path, 'metadata.json'), 'r') as fobj:
        assert json.load(fobj) == node.metadata()


def test_archive_addon_not_implemented(node):
    addon = node.addons[0]
    addon.addon = 'FakeService'
    with pytest.raises(NotImplementedError) as err:
        archive_addon(addon)
    assert err.type == NotImplementedError


def test_archive_addon_called(monkeypatch, node, ctrl_tempdir, patch_callback):
    mock_addon_archive = mock.MagicMock()
    monkeypatch.setattr('archiver.worker.tasks.archival.archive_addon', mock_addon_archive)

    assert len(node.addons) == 1
    addon = node.addons[0]
    assert addon.addon == 'github'

    archive(node)

    assert patch_callback.called
    mock_addon_archive.si.assert_called_once()
    mock_addon_archive.si.assert_called_once_with(addon)


def test_archive_addons_called(monkeypatch, node_many_addons, ctrl_tempdir, patch_callback):
    mock_addon_archive = mock.MagicMock()
    monkeypatch.setattr('archiver.worker.tasks.archival.archive_addon', mock_addon_archive)

    assert len(node_many_addons.addons) > 1

    archive(node_many_addons)

    assert patch_callback.called

    calls = [mock.call(addon) for addon in node_many_addons.addons]
    mock_addon_archive.si.assert_has_calls(calls, any_order=True)


def test_archive_child(monkeypatch, node_with_child, ctrl_tempdir, patch_callback):
    mock_child_archive = mock.MagicMock()
    monkeypatch.setattr('archiver.worker.tasks.archive', mock_child_archive)
    #Dont clone addons
    monkeypatch.setattr('archiver.worker.tasks.archival.archive_addon', mock.MagicMock())

    assert len(node_with_child.children) == 1
    child = node_with_child.children[0]

    archive(node_with_child)

    assert patch_callback.called
    mock_child_archive.si.assert_called_once()
    mock_child_archive.si.assert_called_once_with(child)


def test_archive_many_children(monkeypatch, node_with_children, ctrl_tempdir, patch_callback):
    mock_child_archive = mock.MagicMock()
    monkeypatch.setattr('archiver.worker.tasks.archival.create_archive.run', mock_child_archive)
    #Dont clone addons
    monkeypatch.setattr('archiver.worker.tasks.archival.archive_addon.run', lambda *_, **__: None)

    assert len(node_with_children.children) > 1

    archive(node_with_children)

    assert patch_callback.called

    calls = collect_children_calls(node_with_children)
    mock_child_archive.assert_has_calls(calls, any_order=True)
    assert len(calls) == len(mock_child_archive.mock_calls)


def test_archive_nest_children(monkeypatch, node_nested_children, ctrl_tempdir, patch_callback):
    mock_child_archive = mock.MagicMock()
    monkeypatch.setattr('archiver.worker.tasks.archival.create_archive.run', mock_child_archive)
    #Dont clone addons
    monkeypatch.setattr('archiver.worker.tasks.archival.archive_addon.run', lambda *_, **__: None)

    assert len(node_nested_children.children) > 1

    archive(node_nested_children)

    assert patch_callback.called

    calls = collect_children_calls(node_nested_children)
    assert len(calls) > 2
    # assert mock_child_archive.si.mock_calls == calls

    mock_child_archive.assert_has_calls(calls, any_order=True)
    assert len(calls) == len(mock_child_archive.mock_calls)


# def test_archive_children_addons(monkeypatch, node_children_addons, ctrl_tempdir, patch_callback):
#     mock_child_archive = mock.MagicMock()
#     mock_addon_archive = mock.MagicMock()
#     monkeypatch.setattr('archiver.worker.tasks.archival.create_archive', mock_child_archive)
#     monkeypatch.setattr('archiver.worker.tasks.archival.archive_addon', mock_addon_archive)

#     assert len(node_nested_children.children) > 1

#     archive(node_nested_children)

#     assert patch_callback.called

#     mock_child_archive.si.assert_has_calls(collect_children_calls(node_children_addons), any_order=True)


def collect_addon_calls(node):
    addon_calls = [mock.call(addon) for addon in node.addons]
    addon_calls.extend([collect_addon_calls(child) for child in node.children])
    return addon_calls


def collect_children_calls(node):
    kid_calls = [mock.call(node)]
    for child in node.children:
        # kid_calls.append(mock.call(child))
        kid_calls.extend(collect_children_calls(child))
    return kid_calls


# @mock.patch('archiver.worker.tasks.archival.archive_addon')
# def test_archive_github(mock_archive, node, monkeypatch, ctrl_tempdir):
#     addon = node.addons[0]

#     # def git_mock(*args, **_):

#     #     assert args[1][0] == 'git'

#     #     if args[1][1] == 'pull':
#     #         assert args[1][2] == '--all'
#     #     elif args[1][1] == 'fetch':
#     #         assert args[1][2] == '--all'
#     #     elif args[1][1] == 'clone':
#     #         assert addon['access_token'] in args[1][2]
#     #         assert addon['user'] in args[1][2]
#     #         assert addon['repo'] in args[1][2]
#     #     elif args[1][1] == 'branch':
#     #         return ''

#     git_mock = mock.Mock(return_value='')
#     assert addon.addon == 'github'
#     monkeypatch.setattr('archiver.worker.tasks.archival.github_clone.Git.execute', git_mock)
#     with pytest.raises(IOError) as err:
#         archive_addon(addon)
#     assert err.type == IOError
#     assert err.value.errno == 2
