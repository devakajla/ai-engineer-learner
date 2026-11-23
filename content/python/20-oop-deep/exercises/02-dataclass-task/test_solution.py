import dataclasses

import pytest

from solution import Task, TaskId


def test_defaults_and_strip():
    t = Task("  Write tests ")
    assert (t.title, t.priority, t.tags, t.done) == ("Write tests", 2, [], False)
    assert dataclasses.is_dataclass(Task)


def test_tags_not_shared():
    a = Task("a")
    a.tags.append("x")
    assert Task("b").tags == []


def test_validation():
    with pytest.raises(ValueError):
        Task("   ")
    with pytest.raises(ValueError):
        Task("x", priority=5)


def test_sorting():
    tasks = sorted([Task("b", 2), Task("a", 2), Task("z", 1)])
    assert [t.title for t in tasks] == ["z", "a", "b"]


def test_frozen_id():
    tid = TaskId(5)
    assert {tid: 1}[TaskId(5)] == 1
    with pytest.raises(dataclasses.FrozenInstanceError):
        tid.value = 6
