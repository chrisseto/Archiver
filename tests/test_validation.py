import pytest

from archiver.datatypes import Node
from archiver.datatypes.validation import validate_project, ValidationError

from utils import jsons


def test_empty():
    with pytest.raises(ValidationError) as exc:
        validate_project(jsons.empty)
    assert exc.type == ValidationError
    assert exc.value.reason == 'missing node segment'


def test_bad_structure():
    with pytest.raises(ValidationError) as exc:
        validate_project(jsons.bad_structure)
    assert exc.type == ValidationError
    assert exc.value.reason == 'missing node segment'


def test_bad_service():
    # TODO
    pass


def test_success():
    assert validate_project(jsons.good)


def test_node_creation():
    node = Node.from_json(jsons.good)
    assert isinstance(node, Node)
    assert node.is_child is False
    assert node.raw_json == jsons.good['node']


def test_service_creation():
    node = Node.from_json(jsons.good)
    assert len(node.services) == 1
    service = node.services[0]
    assert service
    assert service.service == 'github'
    assert service['user'] == 'chrisseto'
    assert service.parent == node


# Disclaimer: node probably is not good with children
# But does in fact have children
def test_node_children():
    node = Node.from_json(jsons.good_with_children)
    assert len(node.children) == 1
    child = node.children[0]
    assert child
    assert len(child.children) == 0
    assert child.is_child
    assert node == child.parent
