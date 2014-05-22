import pytest

from webtest import TestApp

from archiver.foreman import utils, build_app

from utils.jsons import good


@pytest.fixture(autouse=True, scope='session')
def app(request):
    return TestApp(build_app())


@pytest.fixture(autouse=True)
def patch_push(monkeypatch):
    monkeypatch.setattr(utils, 'push_task', lambda *_, **__: None)


def test_empty(app):
    ret = app.post('/', expect_errors=True)
    assert ret.status_code == 400


def test_empty_put(app):
    ret = app.put('/', expect_errors=True)
    assert ret.status_code == 400


def test_empty_json(app):
    ret = app.post_json('/', {}, expect_errors=True)
    assert ret.status_code == 400


def test_good_json(app):
    ret = app.post_json('/', good)
    assert ret.status_code == 201
