import pytest

from solution import get_prompt

REGISTRY = {"qa": {"v1": "A", "v2": "B", "v10": "C"}, "sum": {"v1": "S1"}}


def test_with_version():
    assert get_prompt(REGISTRY, "qa", "v1") == "A"
    assert get_prompt(REGISTRY, "qa", "v2") == "B"


def test_latest_uses_numbers_not_text():
    assert get_prompt(REGISTRY, "qa") == "C", "v10 is later than v2"
    assert get_prompt(REGISTRY, "sum") == "S1"


def test_unknown_name_and_version():
    with pytest.raises(KeyError):
        get_prompt(REGISTRY, "zzz")
    with pytest.raises(KeyError):
        get_prompt(REGISTRY, "qa", "v99")


def test_order_in_dict_does_not_matter():
    registry = {"x": {"v3": "three", "v1": "one", "v2": "two"}}
    assert get_prompt(registry, "x") == "three"
