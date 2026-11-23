from solution import estimate_tokens


def test_examples():
    assert estimate_tokens("hello world") == 3
    assert estimate_tokens("abcd") == 1
    assert estimate_tokens("") == 0


def test_edges():
    assert estimate_tokens("a") == 1, "even 1 character needs 1 token"
    assert estimate_tokens("abcde") == 2, "5 characters round up to 2"
    assert estimate_tokens("a" * 400) == 100
    assert isinstance(estimate_tokens("abc"), int), "return an int, not a float"
