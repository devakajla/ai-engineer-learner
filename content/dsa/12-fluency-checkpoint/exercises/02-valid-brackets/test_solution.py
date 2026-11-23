from solution import valid_brackets


def test_examples():
    assert valid_brackets("([]{})") is True
    assert valid_brackets("(]") is False
    assert valid_brackets("((") is False


def test_more():
    assert valid_brackets("") is True
    assert valid_brackets(")") is False, "close with nothing open"
    assert valid_brackets("()[]{}") is True
    assert valid_brackets("([)]") is False
    assert valid_brackets("{[()]}") is True
