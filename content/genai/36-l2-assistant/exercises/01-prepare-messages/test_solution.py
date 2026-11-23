import pytest

from solution import prepare_messages

REGISTRY = {
    "tutor": {"v1": "You are a {level} tutor.", "v2": "You are a {level} tutor. Be brief."},
}


def test_basic():
    out = prepare_messages(REGISTRY, "tutor", {"level": "kind"}, "What is a list?", version="v1")
    assert out == [
        {"role": "system", "content": "You are a kind tutor."},
        {"role": "user", "content": "What is a list?"},
    ]


def test_newest_version_by_default():
    out = prepare_messages(REGISTRY, "tutor", {"level": "kind"}, "Hi")
    assert out[0]["content"] == "You are a kind tutor. Be brief.", "default is the newest version"


def test_examples_between_system_and_question():
    out = prepare_messages(REGISTRY, "tutor", {"level": "x"}, "3+3?", examples=[("2+2", "4"), ("1+1", "2")], version="v1")
    roles = [m["role"] for m in out]
    assert roles == ["system", "user", "assistant", "user", "assistant", "user"]
    assert out[1]["content"] == "2+2" and out[2]["content"] == "4"
    assert out[-1] == {"role": "user", "content": "3+3?"}


def test_none_and_empty_examples():
    a = prepare_messages(REGISTRY, "tutor", {"level": "x"}, "Hi", examples=None, version="v1")
    b = prepare_messages(REGISTRY, "tutor", {"level": "x"}, "Hi", examples=[], version="v1")
    assert a == b and len(a) == 2


def test_missing_value():
    with pytest.raises(ValueError, match="level"):
        prepare_messages(REGISTRY, "tutor", {}, "Hi")


def test_examples_not_changed():
    examples = [("a", "b")]
    prepare_messages(REGISTRY, "tutor", {"level": "x"}, "Hi", examples=examples)
    assert examples == [("a", "b")]
