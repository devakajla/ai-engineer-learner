from solution import content_hash, plan_sync


def test_all_four():
    stored = {"a": content_hash("old"), "b": content_hash("same"), "gone": "x"}
    docs = {"a": "new", "b": "same", "c": "fresh"}
    assert plan_sync(stored, docs) == {"add": ["c"], "update": ["a"], "delete": ["gone"], "same": ["b"]}


def test_empty_both():
    assert plan_sync({}, {}) == {"add": [], "update": [], "delete": [], "same": []}


def test_first_run_adds_all_sorted():
    out = plan_sync({}, {"b": "1", "a": "2"})
    assert out["add"] == ["a", "b"]


def test_whitespace_change_is_same():
    stored = {"a": content_hash("hello world")}
    assert plan_sync(stored, {"a": "hello   world\n"})["same"] == ["a"]


def test_everything_removed():
    out = plan_sync({"x": "h", "y": "h"}, {})
    assert out["delete"] == ["x", "y"]
