import copy

import mock

import pytest

from archiver.datatypes import Container
from archiver.worker.tasks.archivers import get_archiver
from archiver.worker.tasks.archivers.s3_archiver import S3Archiver

from utils import jsons


@pytest.fixture(autouse=True)
def patch_s3(monkeypatch):
    monkeypatch.setattr('archiver.worker.tasks.archivers.s3_archiver.S3Connection.get_bucket', lambda *_, **__: None)


@pytest.fixture
def patch_push(monkeypatch):
    patched = mock.MagicMock()
    monkeypatch.setattr('archiver.worker.tasks.archivers.s3_archiver.store.push_file', patched)
    return patched


@pytest.fixture
def s3_container():
    return Container.from_json(jsons.good_multi_service)


@pytest.fixture
def s3_service():
    temp = copy.deepcopy(jsons.good_multi_service)
    #Remove github service
    del temp['container']['services'][0]
    return Container.from_json(temp).services[0]


def test_gets_called():
    assert get_archiver('s3') == S3Archiver


def test_iters_bucket_list(monkeypatch, s3_service):
    mock_bucket = mock.MagicMock()
    mock_bucket.list.return_value = [key_factory(k) for k in ['testone', 'testthree', 'TestOther']]
    mock_get_key = mock.MagicMock()
    monkeypatch.setattr('archiver.worker.tasks.archivers.s3_archiver.S3Connection.get_bucket', lambda *_, **__: mock_bucket)
    archiver = S3Archiver(s3_service)
    monkeypatch.setattr(archiver, 'get_key', mock_get_key)

    archiver.clone()
    kalls = [mock.call(kall) for kall in mock_bucket.list()]

    mock_get_key.assert_has_calls(kalls[:2], any_order=True)
    mock_get_key.delay.assert_called_once_with(mock_bucket.list()[2])


def test_pushes_files(s3_service, patch_push):
    mock_key = mock.MagicMock()
    mock_key.key = 'TestKey'
    archiver = S3Archiver(s3_service)
    archiver.get_key(mock_key)
    kall = (archiver.build_directories('TestKey'))
    patch_push.assert_called_once_with(*kall)


def test_resource_pulled(s3_service):
    bucket = s3_service['bucket']
    a = S3Archiver(s3_service)
    assert S3Archiver.RESOURCE == 'bucket'
    assert bucket in a.dirinfo['prefix']


def key_factory(val):
    mock_key = mock.MagicMock()
    if 'T' in val:
        mock_key.size = 5242880000
    else:
        mock_key.size = 10
    mock_key.key = val
    return mock_key
