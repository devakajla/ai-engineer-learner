import pytest

from solution import step_efficiency, tool_names, trajectory_match


def test_tool_names_only_from_tool_spans_in_order():
    trace = [{"name": "llm", "kind": "llm"}, {"name": "search", "kind": "tool"},
             {"name": "llm", "kind": "llm"}, {"name": "calc", "kind": "tool"}]
    assert tool_names(trace) == ["search", "calc"]
    assert tool_names([]) == []


def test_exact_mode():
    assert trajectory_match(["search", "calc"], ["search", "calc"]) is True
    assert trajectory_match(["search", "calc", "calc"], ["search", "calc"]) is False
    assert trajectory_match(["calc", "search"], ["search", "calc"]) is False


def test_in_order_mode_allows_extra_steps_between():
    assert trajectory_match(["search", "log", "calc"], ["search", "calc"], "in_order") is True
    assert trajectory_match(["calc", "search"], ["search", "calc"], "in_order") is False
    assert trajectory_match(["search"], ["search", "calc"], "in_order") is False
    assert trajectory_match(["a"], [], "in_order") is True


def test_in_order_mode_counts_repeats_correctly():
    assert trajectory_match(["a", "b"], ["a", "a"], "in_order") is False
    assert trajectory_match(["a", "b", "a"], ["a", "a"], "in_order") is True


def test_any_order_mode():
    assert trajectory_match(["calc", "x", "search"], ["search", "calc"], "any_order") is True
    assert trajectory_match(["search"], ["search", "calc"], "any_order") is False


def test_unknown_mode_raises():
    with pytest.raises(ValueError, match="unknown mode: loose"):
        trajectory_match([], [], "loose")


def test_step_efficiency():
    assert step_efficiency(["a", "b"], ["a", "b"]) == 1.0
    assert step_efficiency(["a", "b", "c", "d"], ["a", "b"]) == 0.5
    assert step_efficiency(["a"], ["a", "b"]) == 1.0, "never more than 1.0"
    assert step_efficiency([], []) == 1.0
    assert step_efficiency([], ["a"]) == 0.0
    assert step_efficiency(["a", "b", "c"], ["a"]) == 0.33
