import json

import mock

import pytest

from archiver import settings
from archiver.datatypes import Container
from archiver.worker.tasks import callbacks
from archiver.worker.tasks.archivers import get_archiver
from archiver.worker.tasks.archivers.s3_archiver import S3Archiver

from utils import jsons


@pytest.fixture
def container():
    return Container.from_json(jsons.good_multi_service)


@pytest.fixture
def container_children():
    return Container.from_json(jsons.good_with_children)


@pytest.fixture(autouse=True)
def eat_callbacks(monkeypatch):
    mock_requests = mock.Mock()
    monkeypatch.setattr('archiver.worker.tasks.callbacks.requests', mock_requests)
    return mock_requests


def test_gen_manifest(container):
    manifest = callbacks.generate_manifest([], [], container)
    assert 'metadata' in manifest.keys()
    assert 'storedAt' in manifest.keys()
    assert 'services' in manifest.keys()
    assert 'children' in manifest.keys()


def test_returns_with_children(container_children):
    ret = callbacks.archival_finish([], container_children.children[0])
    assert ret is not None


def test_callback_payload(container, eat_callbacks):
    ret = callbacks.archival_finish([], container)
    for call in eat_callbacks.post.call_args_list:
        #*args, args[0]
        assert call[0][0] in settings.CALLBACK_ADDRESSES
        data = json.loads(call[1]['data'])
        assert data['id'] == container.id
        assert data['status'] == 'success'


def test_failed_callback_payload(container, eat_callbacks):
    ret = callbacks.archival_finish([Exception('Testing')], container)
    for call in eat_callbacks.post.call_args_list:
        #*args, args[0]
        assert call[0][0] in settings.CALLBACK_ADDRESSES
        data = json.loads(call[1]['data'])
        assert data['id'] == container.id
        assert data['status'] == 'failed'
        assert len(data['reasons']) == 1
        assert data['reasons'][0] == 'Testing'


def test_parse_basic_auth():
    url = 'http://User:Pass@website.com'
    assert callbacks.parse_auth(url) == ('User', 'Pass')

def test_parse_basic_auth_https():
    url = 'https://User:Pass@website.com'
    assert callbacks.parse_auth(url) == ('User', 'Pass')


def test_parse_basic_auth_no_pass():
    url = 'https://User@website.com'
    assert callbacks.parse_auth(url) == ('User', '')

def test_parse_basic_auth_none():
    url = 'https://website.com'
    assert callbacks.parse_auth(url) == None
