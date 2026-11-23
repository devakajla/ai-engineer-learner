import pytest

from solution import render_prompt

REGISTRY = {"qa": {"v1": "Answer: {question}", "v2": "Answer briefly: {question}", "v10": "Be kind: {question}"}}


def test_latest_version_by_number():
    assert render_prompt(REGISTRY, "qa", {"question": "Hi"}) == "Be kind: Hi", "v10 is later than v2"


def test_given_version():
    assert render_prompt(REGISTRY, "qa", {"question": "Hi"}, version="v1") == "Answer: Hi"
    assert render_prompt(REGISTRY, "qa", {"question": "Hi"}, "v2") == "Answer briefly: Hi"


def test_errors():
    with pytest.raises(KeyError):
        render_prompt(REGISTRY, "zzz", {"question": "Hi"})
    with pytest.raises(KeyError):
        render_prompt(REGISTRY, "qa", {"question": "Hi"}, version="v99")
    with pytest.raises(ValueError, match="missing variable: question"):
        render_prompt(REGISTRY, "qa", {})
