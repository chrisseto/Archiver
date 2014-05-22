import mock

import pytest

from webtest import TestApp

from archiver.datatypes import Node
from archiver.foreman import build_app

from utils.jsons import good


@pytest.fixture(autouse=True)
def patch_push(monkeypatch):
    mock_push = mock.MagicMock()
    monkeypatch.setattr('archiver.foreman.utils.archive.delay', mock_push)
    return mock_push


@pytest.fixture(autouse=True)
def app(request):
    return TestApp(build_app())


def test_empty(app):
    ret = app.post('/', expect_errors=True)
    assert ret.status_code == 400


def test_empty_put(app):
    ret = app.put('/', expect_errors=True)
    assert ret.status_code == 400


def test_empty_json(app):
    ret = app.post_json('/', {}, expect_errors=True)
    assert ret.status_code == 400


def test_good_json(app, patch_push):
    ret = app.post_json('/', good)
    assert ret.status_code == 201
    assert patch_push.call_args[0][0].raw_json == good['node']
