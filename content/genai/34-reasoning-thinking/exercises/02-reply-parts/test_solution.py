from types import SimpleNamespace as NS

from solution import reply_parts


def test_separate_field():
    message = NS(content=" 14 apples ", reasoning=" 23-9=14 ... ")
    assert reply_parts(message) == {"thinking": "23-9=14 ...", "answer": "14 apples"}


def test_think_tags_in_content():
    message = NS(content="<think>x</think>14 apples")
    assert reply_parts(message) == {"thinking": "x", "answer": "14 apples"}, (
        "a message without a reasoning attribute must still work"
    )


def test_reasoning_is_none_or_empty():
    assert reply_parts(NS(content="<think>x</think>y", reasoning=None)) == {"thinking": "x", "answer": "y"}
    assert reply_parts(NS(content="plain", reasoning="  ")) == {"thinking": "", "answer": "plain"}


def test_content_none():
    assert reply_parts(NS(content=None, reasoning="only thinking")) == {
        "thinking": "only thinking",
        "answer": "",
    }
    assert reply_parts(NS(content=None)) == {"thinking": "", "answer": ""}
