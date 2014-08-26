import mock

import pytest

from archiver.foreman import utils
from archiver.datatypes import Container

from utils import jsons

@pytest.fixture
def patch_archive(monkeypatch):
    mock_archive = mock.MagicMock()
    monkeypatch.setattr(utils, 'archive', mock_archive)
    return mock_archive


@pytest.fixture
def container():
    return Container.from_json(jsons.good)


def test_task_created(patch_archive, container):
    ret = utils.push_task(container)
    assert 'STARTED' in ret['response']['status']
    assert ret['status'] == 201  # Created
    patch_archive.delay.assert_called_once_with(container)


def test_returns_error(patch_archive, container):
    patch_archive.delay.side_effect = Exception()
    ret = utils.push_task(container)
    assert 'ERROR' in ret['response']['status']
    assert ret['status'] == 500
    patch_archive.delay.assert_called_once_with(container)
