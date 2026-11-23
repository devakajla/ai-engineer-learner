from typing import get_args, get_type_hints

import pytest

import solution
from solution import next_status, parse_task


def test_types_defined():
    assert set(get_args(solution.Status)) == {"todo", "doing", "done"}
    hints = get_type_hints(solution.TaskDict)
    assert hints["id"] is int and hints["title"] is str and hints["status"] == solution.Status


def test_next_status():
    assert [next_status(s) for s in ("todo", "doing", "done")] == ["doing", "done", "done"]


def test_parse_task():
    assert parse_task({"id": 1, "title": "x", "status": "done"}) == {"id": 1, "title": "x", "status": "done"}
    for bad in (
        {"id": "1", "title": "x", "status": "done"},
        {"id": 1, "title": "", "status": "done"},
        {"id": 1, "title": "x", "status": "blocked"},
        {"title": "x", "status": "todo"},
    ):
        with pytest.raises(ValueError):
            parse_task(bad)
