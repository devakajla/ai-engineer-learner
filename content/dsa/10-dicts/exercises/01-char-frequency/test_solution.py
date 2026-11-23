from solution import char_frequency


def test_examples():
    assert char_frequency("aab") == {"a": 2, "b": 1}
    assert char_frequency("") == {}


def test_more():
    assert char_frequency("hello") == {"h": 1, "e": 1, "l": 2, "o": 1}
    assert char_frequency("Aa") == {"A": 1, "a": 1}, "case matters"
    assert char_frequency("a b") == {"a": 1, " ": 1, "b": 1}
