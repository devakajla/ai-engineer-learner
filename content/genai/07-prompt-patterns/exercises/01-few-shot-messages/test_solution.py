from solution import few_shot_messages


def test_examples():
    assert few_shot_messages("Label the sentiment.", [("I love it", "positive")], "So bad") == [
        {"role": "system", "content": "Label the sentiment."},
        {"role": "user", "content": "I love it"},
        {"role": "assistant", "content": "positive"},
        {"role": "user", "content": "So bad"},
    ]
    assert few_shot_messages("Be brief.", [], "Hi") == [
        {"role": "system", "content": "Be brief."},
        {"role": "user", "content": "Hi"},
    ]


def test_order_of_several_examples():
    result = few_shot_messages("S", [("a", "1"), ("b", "2")], "q")
    assert [m["content"] for m in result] == ["S", "a", "1", "b", "2", "q"], "keep the order of the examples"
    assert [m["role"] for m in result] == ["system", "user", "assistant", "user", "assistant", "user"]


def test_input_is_not_changed():
    examples = [("a", "1")]
    few_shot_messages("S", examples, "q")
    assert examples == [("a", "1")]
