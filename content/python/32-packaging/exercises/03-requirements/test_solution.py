import pytest

from solution import merge_requirements, split_requirement


def test_split_simple():
    assert split_requirement("httpx") == ("httpx", "")


def test_split_with_rule():
    assert split_requirement("fastapi>=0.110,<1.0") == ("fastapi", ">=0.110,<1.0")


def test_split_normalises():
    assert split_requirement("Typing_Extensions >= 4.0, < 5") == ("typing-extensions", ">=4.0,<5")


def test_split_no_name():
    with pytest.raises(ValueError):
        split_requirement(">=1.0")
    with pytest.raises(ValueError):
        split_requirement("")


def test_merge_new_wins_and_sorted():
    out = merge_requirements(["httpx>=0.20", "fastapi"], ["HTTPX>=0.27", "pytest"])
    assert out == ["fastapi", "httpx>=0.27", "pytest"]


def test_merge_empty():
    assert merge_requirements([], []) == []
    assert merge_requirements(["b", "a"], []) == ["a", "b"]


def test_merge_same_name_different_spelling():
    assert merge_requirements(["typing_extensions"], ["Typing-Extensions>=4"]) == ["typing-extensions>=4"]


def test_inputs_not_changed():
    existing = ["b", "a"]
    new = ["c"]
    merge_requirements(existing, new)
    assert existing == ["b", "a"] and new == ["c"]
