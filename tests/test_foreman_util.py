import mock

import pytest

from archiver.foreman import utils, build_app
from archiver.datatypes import Container

from utils import jsons


@pytest.fixture(autouse=True, scope='session')
def app(request):
    return build_app()


@pytest.fixture
def patch_archive(monkeypatch):
    mock_archive = mock.MagicMock()
    monkeypatch.setattr(utils, 'archive', mock_archive)
    return mock_archive


@pytest.fixture
def container():
    return Container.from_json(jsons.good)


def test_task_created(patch_archive, container, app):
    with app.test_request_context():
        ret = utils.push_task(container)
        assert 'STARTED' in ret.response[0]
        assert ret.status_code == 201  # Created
        patch_archive.delay.assert_called_once_with(container)


def test_returns_error(patch_archive, container, app):
    patch_archive.delay.side_effect = Exception()
    with app.test_request_context():
        ret = utils.push_task(container)
        assert 'ERROR' in ret.response[0]
        assert ret.status_code == 500
        patch_archive.delay.assert_called_once_with(container)
