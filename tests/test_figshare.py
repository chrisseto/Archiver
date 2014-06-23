import copy

import mock

import pytest


from archiver.datatypes import Container
from archiver.worker.tasks.archivers import get_archiver
from archiver.worker.tasks.archivers.figshare_archiver import FigshareArchiver
from utils import jsons
from utils.clients import MockClient


@pytest.fixture
def figshare_project():
    return Container.from_json(jsons.good_multi_service)


@pytest.fixture
def client(monkeypatch):
    client = MockClient()
    monkeypatch.setattr('archiver.worker.tasks.archivers.figshare_archiver.client', lambda *_, **__: client)
    return client


@pytest.fixture
def figshare_service():
    return Container.from_json(jsons.container_with_figshare).services[0]


def test_gets_called():
    assert get_archiver('figshare') == FigshareArchiver


def test_(monkeypatch, figshare_service):
    mock_download = mock.MagicMock()
    archiver = FigshareArchiver(figshare_service)
    monkeypatch.setattr(archiver.download_file, 'si', mock_download)
    # archiver.clone()
    # assert mock_download.called



# @pytest.mark.usesfixtures('push_file')
# @pytest.mark.usesfixtures('push_json')
# def test_pushes_files(figshare_service, push_file, push_json):
#     mock_key = MockId()
#     archiver = FigshareArchiver(figshare_service)
#     key, meta = archiver.get_key(archiver, mock_key)
#     assert key == mock_key
#     assert len(push_file.mock_calls) == 1
#     assert len(push_json.mock_calls) == 1
#     assert push_json.called


