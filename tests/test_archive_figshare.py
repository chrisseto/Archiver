import copy

import mock

import pytest

from archiver.datatypes import Container
from archiver import exceptions
from archiver.worker.tasks.archivers import get_archiver
from archiver.worker.tasks.archivers import figshare_archiver
from archiver.worker.tasks.archivers.figshare_archiver import FigshareArchiver

from utils import jsons
from utils.clients import MockClient


@pytest.fixture
def figshare_container():
    return Container.from_json(jsons.good_multi_service)


@pytest.fixture
def client(monkeypatch):
    client = MockClient()
    monkeypatch.setattr('archiver.worker.tasks.archivers.figshare_archiver.client', lambda *_, **__: client)
    return client


@pytest.fixture
def figshare_service():
    return Container.from_json(jsons.container_with_figshare).services[0]


@pytest.fixture
def fsarchiver(figshare_service):
    return FigshareArchiver(figshare_service)


def test_gets_called():
    assert get_archiver('figshare') == FigshareArchiver


def test_exceptions_on_malformed(figshare_service):
    copied = copy.deepcopy(figshare_service)
    del copied.raw_json['token_key']

    with pytest.raises(exceptions.FigshareArchiverError) as e:
        FigshareArchiver(copied)

    assert 'token' in e.value.message


def test_exception_on_no_keys(monkeypatch, figshare_service):
    monkeypatch.setattr(figshare_archiver, 'FIGSHARE_OAUTH_TOKENS', [None, None])

    with pytest.raises(exceptions.FigshareKeyError) as e:
        FigshareArchiver(figshare_service)

    assert 'OAuth' in e.value.message


def test_figshare_404(monkeypatch, fsarchiver):
    mock_resp = mock.Mock()
    mock_resp.ok.return_value = False
    mock_resp.status_code = 404
    mock_resp.json.side_effect = ValueError
    monkeypatch.setattr(figshare_archiver.requests, 'get', mock_resp)

    with pytest.raises(exceptions.FigshareArchiverError):
        fsarchiver.is_project()

    with pytest.raises(exceptions.FigshareArchiverError):
        fsarchiver.get_article_files()

    with pytest.raises(exceptions.FigshareArchiverError):
        fsarchiver.get_project_articles()


def test_on_cannot_connect(fsarchiver, monkeypatch):
    mock_resp = mock.Mock()
    mock_resp.ok.return_value = False
    monkeypatch.setattr(figshare_archiver.requests, 'get', mock_resp)

    with pytest.raises(exceptions.FigshareArchiverError):
        fsarchiver.is_project()


def test_figshare_errors():
    pass  # TODO


def test_unfetchable(monkeypatch, fsarchiver):

    with pytest.raises(exceptions.UnfetchableFile):
        figshare_archiver.download_file(fsarchiver, {'name': 'bogusname'}, 23)


def test_retry(monkeypatch, fsarchiver):
    mock_resp = mock.Mock()
    mock_resp.side_effect = ValueError
    monkeypatch.setattr(figshare_archiver.requests, 'get', mock_resp)

    dlf = copy.copy(figshare_archiver.download_file)
    mock_download = mock.MagicMock()
    mock_download.side_effect = dlf
    mock_download.retry.side_effect = dlf.retry
    monkeypatch.setattr(figshare_archiver, 'download_file', mock_download)

    fdict = {
        'download_url': 'test'
    }

    with pytest.raises(ValueError):
        figshare_archiver.download_file(fsarchiver, fdict, 23)

    assert mock_download.mock_calls > 2
