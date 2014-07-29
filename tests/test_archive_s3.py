import copy

import mock

import pytest

from celery import chord

from archiver import settings, exceptions
from archiver.datatypes import Container
from archiver.worker.tasks.archivers import get_archiver
from archiver.worker.tasks.archivers.s3_archiver import S3Archiver

from utils import jsons
from utils.clients import MockBucket, MockKey


@pytest.fixture
def s3_container():
    return Container.from_json(jsons.good_multi_service)


@pytest.fixture(autouse=True)
def bucket(monkeypatch):
    bucket = MockBucket()
    monkeypatch.setattr('archiver.worker.tasks.archivers.s3_archiver.S3Connection.get_bucket', lambda *_, **__: bucket)
    return bucket


@pytest.fixture
def s3_service():
    temp = copy.deepcopy(jsons.good_multi_service)
    #Remove github service
    del temp['container']['services'][0]
    return Container.from_json(temp).services[0]


@pytest.fixture
def s3archiver(s3_service):
    return S3Archiver(s3_service)


def test_gets_called():
    assert get_archiver('s3') == S3Archiver


def test_iters_bucket_list(monkeypatch, s3_service, bucket):
    mock_get_key = mock.MagicMock()
    archiver = S3Archiver(s3_service)
    monkeypatch.setattr(archiver.get_key, 'si', mock_get_key)
    archiver.clone()
    kalls = [mock.call(archiver, key) for key in bucket.get_all_versions()]
    mock_get_key.assert_has_calls(kalls[:2], any_order=True)


@pytest.mark.usesfixtures('push_file')
@pytest.mark.usesfixtures('push_json')
def test_pushes_files(s3_service, push_file, push_json):
    mock_key = MockKey()
    archiver = S3Archiver(s3_service)
    key, meta = archiver.get_key(archiver, mock_key)
    assert key == mock_key
    assert len(push_file.mock_calls) == 1
    assert len(push_json.mock_calls) == 1
    assert push_json.called


def test_returns_flat_list(s3archiver):
    ret = s3archiver.clone()
    assert isinstance(ret, chord)
    for notlist in ret.task:
        assert not isinstance(notlist, list)


def test_returns_flat_list_versioned(s3archiver):
    s3archiver.versions = True
    ret = s3archiver.clone()
    assert isinstance(ret, chord)
    for notlist in ret.task:
        assert not isinstance(notlist, list)


def test_key_too_large(s3archiver):
    settings.MAX_FILE_SIZE = 500
    mock_key = MockKey()
    mock_key.size = 700

    with pytest.raises(exceptions.archivers.FileTooLargeError) as e:
        s3archiver.get_key(s3archiver, mock_key)
    assert e.value.file == mock_key.key
    settings.MAX_FILE_SIZE = None
