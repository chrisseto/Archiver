import copy

import mock

import pytest

from archiver import celery
from archiver.backend import store
from archiver.settings import FIGSHARE_OAUTH_TOKENS

from utils import jsons
from utils.clients import MockProject, MockId


@pytest.fixture
def figshare_project():
    return Project.from_json(jsons.good_multi_service)


@pytest.fixture
def project(monkeypatch):
    Project = MockProject()
    monkeypatch.setattr('archiver.worker.tasks.archivers.fighare_archiver.FighareConnection.get_project', lambda *_, **__: project)
    return project


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


def test_resource_pulled(s3_service):
    assert S3Archiver.RESOURCE == 'bucket'
