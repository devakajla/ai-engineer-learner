from solution import word_lengths


def test_examples():
    assert word_lengths(["hi", "hello"]) == {"hi": 2, "hello": 5}
    assert word_lengths([]) == {}


def test_more():
    assert word_lengths(["a", "a"]) == {"a": 1}
    assert word_lengths([""]) == {"": 0}
