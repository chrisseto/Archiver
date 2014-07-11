import mock

import pytest

from archiver import settings
settings.CELERY_ALWAYS_EAGER = True

from archiver import exceptions
from archiver.datatypes import Container
from archiver.worker.tasks.archivers import get_archiver
from archiver.worker.tasks.archivers.dataverse_archiver import DataverseArchiver

from utils import jsons


@pytest.fixture
def dataverse_service():
    return Container.from_json(jsons.good_with_dataverse).services[0]


@pytest.fixture
def dataverse_container():
    return Container.from_json(jsons.good_with_dataverse)


@pytest.fixture
def dvarchiver(dataverse_service):
    return DataverseArchiver(dataverse_service)


def test_gets_called():
    assert get_archiver('dataverse') == DataverseArchiver
    assert get_archiver('dataverse').ARCHIVES == 'dataverse'


def test_host_override(dataverse_service):
    dataverse_service.raw_json['host'] = 'Myfakedataverse.com'
    archiver = DataverseArchiver(dataverse_service)
    assert archiver.host == 'Myfakedataverse.com'


def test_exception_on_malform(dataverse_service):
    del dataverse_service.raw_json['password']

    with pytest.raises(exceptions.DataverseArchiverError) as e:
        DataverseArchiver(dataverse_service)

    assert 'password' in e.value.message
