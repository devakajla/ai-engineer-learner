import pytest

from solution import by_age_desc_name, has_minor, names_by_id, oldest_active

USERS = [
    {"name": "bo", "age": 31, "active": False},
    {"name": "Dev", "age": 22, "active": True},
    {"name": "ana", "age": 31, "active": True},
    {"name": "Cid", "age": 17, "active": True},
]


def test_sort():
    original = [dict(u) for u in USERS]
    names = [u["name"] for u in by_age_desc_name(USERS)]
    assert names == ["ana", "bo", "Dev", "Cid"]
    assert USERS == original, "don't mutate the input"


def test_oldest_active():
    assert oldest_active(USERS)["name"] == "ana"
    assert oldest_active([{"name": "x", "age": 1, "active": False}]) is None
    assert oldest_active([]) is None


def test_has_minor():
    assert has_minor(USERS) is True
    assert has_minor(USERS[:3]) is False


def test_names_by_id():
    assert names_by_id([1, 2], ["a", "b"]) == {1: "a", 2: "b"}
    with pytest.raises(ValueError):
        names_by_id([1, 2, 3], ["a", "b"])
