import pytest

from solution import rest_endpoint


def test_collection_actions():
    assert tuple(rest_endpoint("list", "tasks")) == ("GET", "/tasks")
    assert tuple(rest_endpoint("create", "tasks")) == ("POST", "/tasks")


def test_item_actions():
    assert tuple(rest_endpoint("read", "tasks", 1)) == ("GET", "/tasks/1")
    assert tuple(rest_endpoint("replace", "users", 9)) == ("PUT", "/users/9")
    assert tuple(rest_endpoint("update", "tasks", 42)) == ("PATCH", "/tasks/42")
    assert tuple(rest_endpoint("delete", "tasks", 3)) == ("DELETE", "/tasks/3")


def test_errors():
    with pytest.raises(ValueError):
        rest_endpoint("read", "tasks")
    with pytest.raises(ValueError):
        rest_endpoint("archive", "tasks", 1)
