import mock

import pytest

from webtest import TestApp

from archiver.foreman import build_app

from utils.jsons import good


@pytest.fixture(autouse=True)
def patch_push(monkeypatch):
    mock_push = mock.MagicMock()
    monkeypatch.setattr('archiver.foreman.utils.archive.delay', mock_push)
    return mock_push


@pytest.fixture(autouse=True)
def app(request):
    class ProxyHack(object):
    #http://stackoverflow.com/questions/14872829/get-ip-address-when-testing-flask-application-through-nosetests

        def __init__(self, app):
            self.app = app

        def __call__(self, environ, start_response):
            environ['REMOTE_ADDR'] = environ.get('REMOTE_ADDR', '127.0.0.1')
            return self.app(environ, start_response)

    app = build_app()
    app.wsgi_app = ProxyHack(app.wsgi_app)
    return TestApp(app)


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
    assert patch_push.call_args[0][0].raw_json == good['container']
