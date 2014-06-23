import copy

import mock

import pytest


from archiver.datatypes import Container
from archiver.worker.tasks.archivers import get_archiver
from archiver.worker.tasks.archivers.figshare_archiver import FigshareArchiver
from utils import jsons
from utils.clients import MockId


@pytest.fixture
def figshare_project():
    return Project.from_json(jsons.good_multi_service)


@pytest.fixture
def project(monkeypatch):
    Project = MockId()
    monkeypatch.setattr('archiver.worker.tasks.archivers.fighare_archiver.FighareConnection.get_project', lambda *_, **__: project)
    return project


@pytest.fixture
def figshare_service():
    temp = copy.deepcopy(jsons.good_multi_service)
    #Remove github service
    del temp['container']['services'][0]
    return Container.from_json(temp).services[0]


def test_gets_called():
    assert get_archiver('figshare') == FigshareArchiver


def test_(monkeypatch, figshare_service):
    mock_get_key = mock.MagicMock()
    archiver = FigshareArchiver(figshare_service)
    monkeypatch.setattr(archiver.get_key, 'si', mock_get_key)
    archiver.clone()


@pytest.mark.usesfixtures('push_file')
@pytest.mark.usesfixtures('push_json')
def test_pushes_files(figshare_service, push_file, push_json):
    mock_key = MockId()
    archiver = FigshareArchiver(figshare_service)
    key, meta = archiver.get_key(archiver, mock_key)
    assert key == mock_key
    assert len(push_file.mock_calls) == 1
    assert len(push_json.mock_calls) == 1
    assert push_json.called


