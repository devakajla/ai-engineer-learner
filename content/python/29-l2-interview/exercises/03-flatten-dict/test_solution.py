import inspect

import pytest

import solution
from solution import flatten, unflatten

NESTED = {"db": {"host": "x", "port": 5432, "opts": {"ssl": True}}, "debug": True, "tags": ["a"], "empty": {}}


def test_flatten():
    assert flatten(NESTED) == {"db.host": "x", "db.port": 5432, "db.opts.ssl": True, "debug": True, "tags": ["a"]}
    assert flatten({"a": {"b": 1}}, sep="__") == {"a__b": 1}


def test_uses_generator():
    src = inspect.getsource(solution)
    assert "yield" in src, "use a generator helper"


def test_roundtrip():
    nested = {k: v for k, v in NESTED.items() if k != "empty"}
    assert unflatten(flatten(nested)) == nested


def test_conflicts():
    with pytest.raises(ValueError):
        unflatten({"a": 1, "a.b": 2})
    with pytest.raises(ValueError):
        unflatten({"a.b": 2, "a": 1})
