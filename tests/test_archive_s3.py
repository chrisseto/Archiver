import copy

import mock

import pytest

from archiver.datatypes import Container
from archiver.worker.tasks.archivers import get_archiver
from archiver.worker.tasks.archivers.s3_archiver import S3Archiver

from utils import jsons
from utils.clients import MockBucket, MockKey


@pytest.fixture
def s3_container():
    return Container.from_json(jsons.good_multi_service)


@pytest.fixture
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


def test_gets_called():
    assert get_archiver('s3') == S3Archiver


def test_iters_bucket_list(monkeypatch, s3_service, bucket):
    mock_get_key = mock.MagicMock()
    archiver = S3Archiver(s3_service)
    monkeypatch.setattr(archiver.get_key, 'si', mock_get_key)
    archiver.clone()
    kalls = [mock.call(archiver, key) for key in bucket.get_all_versions()]
    mock_get_key.assert_has_calls(kalls[:2], any_order=True)


@pytest.mark.usesfixtures('patch_push')
def test_pushes_files(s3_service, push_file):
    mock_key = MockKey()
    archiver = S3Archiver(s3_service)
    key, meta = archiver.get_key(archiver, mock_key)
    assert key == mock_key
    assert len(push_file.mock_calls) == 2


def test_resource_pulled(s3_service):
    assert S3Archiver.RESOURCE == 'bucket'
