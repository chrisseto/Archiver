import pytest

from archiver.datatypes import Container
from archiver.datatypes.validation import validate_project, ValidationError

from utils import jsons


def test_empty():
    with pytest.raises(ValidationError) as exc:
        validate_project(jsons.empty)
    assert exc.type == ValidationError
    assert exc.value.reason == 'missing container segment'


def test_bad_structure():
    with pytest.raises(ValidationError) as exc:
        validate_project(jsons.bad_structure)
    assert exc.type == ValidationError
    assert exc.value.reason == 'missing container segment'


def test_bad_service():
    # TODO
    pass


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
