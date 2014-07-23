import copy

import pytest

from archiver.datatypes import Container
from archiver.datatypes.validation import validate_project, ValidationError

from utils import jsons


def test_empty():
    with pytest.raises(ValidationError) as exc:
        validate_project(jsons.empty)
    assert exc.type == ValidationError
    assert exc.value.reason == 'No container field'


def test_unsupported_service():
    to_use = copy.deepcopy(jsons.good)
    to_use['container']['services'].append({
        'Something not there': {}
    })
    with pytest.raises(ValidationError) as exc:
        validate_project(to_use)
    assert exc.type == ValidationError
    assert exc.value.reason == 'Unsupported service Something not there'


def test_unsupported_children_service():
    to_use = copy.deepcopy(jsons.good_with_children)
    to_use['container']['children'][0]['container']['services'].append({
        'Something not there': {}
    })
    with pytest.raises(ValidationError) as exc:
        validate_project(to_use)
    assert exc.type == ValidationError
    assert exc.value.reason == 'Unsupported service Something not there'


def test_bad_child_service():
    to_use = copy.deepcopy(jsons.good_with_children)
    del to_use['container']['children'][0]['container']['services'][0]['github']['access_token']
    with pytest.raises(ValidationError) as exc:
        validate_project(to_use)
    assert exc.type == ValidationError
    assert exc.value.reason == 'Service github is missing field access_token'


def test_bad_structure():
    with pytest.raises(ValidationError) as exc:
        validate_project(jsons.bad_structure)
    assert exc.type == ValidationError
    assert exc.value.reason == 'No container field'


def test_bad_service():
    with pytest.raises(ValidationError) as exc:
        validate_project(jsons.bad_service)
    assert exc.type == ValidationError
    assert exc.value.reason == 'Service github is missing field access_token'


def test_success():
    assert validate_project(jsons.good)


def test_container_creation():
    container = Container.from_json(jsons.good)
    assert isinstance(container, Container)
    assert container.is_child is False
    assert container.raw_json == jsons.good['container']


def test_service_creation():
    container = Container.from_json(jsons.good)
    assert len(container.services) == 1
    service = container.services[0]
    assert service
    assert service.service == 'github'
    assert service['user'] == 'chrisseto'
    assert service.parent == container


# Disclaimer: container probably is not good with children
# But does in fact have children
def test_container_children():
    container = Container.from_json(jsons.good_with_children)
    assert len(container.children) == 1
    child = container.children[0]
    assert child
    assert len(child.children) == 0
    assert child.is_child
    assert container == child.parent
