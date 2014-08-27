import mock

import pytest

from webtest import TestApp

from tornado.web import Application
from tornado.wsgi import WSGIAdapter

from archiver import settings

from archiver.foreman.views import collect_handlers

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

    settings.REQUIRE_AUTH = False
    return TestApp(WSGIAdapter(Application(collect_handlers(), debug=True)))


def test_empty(app):
    url = app.app.application.reverse_url('ArchivesHandler')
    ret = app.post(url, expect_errors=True)
    assert ret.status_code == 400


def test_empty_put(app):
    url = app.app.application.reverse_url('ArchivesHandler')
    ret = app.put(url, expect_errors=True)
    assert ret.status_code == 405


def test_empty_callback(app):
    url = app.app.application.reverse_url('CallbackHandler')
    ret = app.post(url, expect_errors=True)
    assert ret.status_code == 400


def test_empty_json(app):
    url = app.app.application.reverse_url('ArchivesHandler')
    ret = app.post_json(url, {}, expect_errors=True)
    assert ret.status_code == 400


def test_good_json(app, patch_push):
    url = app.app.application.reverse_url('ArchivesHandler')
    ret = app.post_json(url, good)
    assert ret.status_code == 201
    assert patch_push.call_args[0][0].raw_json == good['container']


def test_api_keys_no_auth(app):
    settings.REQUIRE_AUTH = True
    url = app.app.application.reverse_url('ArchivesHandler')
    ret = app.get(url, expect_errors=True)
    assert ret.status_code == 401


def test_api_keys_correct_auth(app):
    settings.REQUIRE_AUTH = True
    settings.API_KEYS = ['MYCOOLAPIKEY']
    app.authorization = ('Basic', ('MYCOOLAPIKEY', ))
    url = app.app.application.reverse_url('ArchivesHandler')
    ret = app.get(url)
    assert ret.status_code == 200


def test_api_keys_incorrect_auth(app):
    settings.REQUIRE_AUTH = True
    settings.API_KEYS = ['MYCOOLAPIKEY']
    app.authorization = ('Basic', ('MYLAMEAPIKEY', ))
    url = app.app.application.reverse_url('ArchivesHandler')
    ret = app.get(url, expect_errors=True)
    assert ret.status_code == 401


def test_api_key_ignores_password(app):
    settings.REQUIRE_AUTH = True
    settings.API_KEYS = ['MYCOOLAPIKEY']
    app.authorization = ('Basic', ('MYCOOLAPIKEY', 'MYLAMEAPIKEY'))
    url = app.app.application.reverse_url('ArchivesHandler')
    ret = app.get(url)
    assert ret.status_code == 200


def test_api_key_ignores_correct_password(app):
    settings.REQUIRE_AUTH = True
    settings.API_KEYS = ['MYCOOLAPIKEY']
    app.authorization = ('Basic', ('MYLAMEAPIKEY', 'MYCOOLAPIKEY'))
    url = app.app.application.reverse_url('ArchivesHandler')
    ret = app.get(url, expect_errors=True)
    assert ret.status_code == 401


def test_api_key_disablable(app):
    settings.REQUIRE_AUTH = False
    url = app.app.application.reverse_url('ArchivesHandler')
    ret = app.get(url)
    assert ret.status_code == 200
