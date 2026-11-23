from solution import parse_json


def test_valid():
    assert parse_json('{"a": 1}') == {"a": 1}
    assert parse_json("[1, 2, 3]") == [1, 2, 3]
    assert parse_json('{"ok": true, "n": null}') == {"ok": True, "n": None}


def test_invalid():
    assert parse_json("hello") is None
    assert parse_json("") is None
    assert parse_json("{'a': 1}") is None, "single quotes are not valid JSON"
    assert parse_json('{"a": 1,}') is None, "a trailing comma is not valid JSON"


def test_not_a_dict_is_fine():
    assert parse_json("5") == 5
    assert parse_json('"hi"') == "hi"
