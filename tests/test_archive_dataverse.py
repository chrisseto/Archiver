import mock

import pytest

from archiver import settings
settings.CELERY_ALWAYS_EAGER = True

from archiver.datatypes import Container
from archiver.worker.tasks.archivers import get_archiver
from archiver.worker.tasks.archivers.dataverse_archiver import DataverseArchiver

from utils import jsons


@pytest.fixture(autouse=True)
def dataverse_service():
    return Container.from_json(jsons.good_with_dataverse).services[0]


@pytest.fixture(autouse=True)
def dataverse_container():
    return Container.from_json(jsons.good_with_dataverse)


def test_gets_called():
    assert get_archiver('dataverse') == DataverseArchiver
    assert get_archiver('dataverse').ARCHIVES == 'dataverse'

#TODO Finish testing
