import random
from solution import is_palindrome


def test_examples():
    assert is_palindrome("level") is True
    assert is_palindrome("ab") is False


def test_edges():
    assert is_palindrome("") is True
    assert is_palindrome("a") is True
    assert is_palindrome("abba") is True


def test_random():
    rng = random.Random(5)
    for _ in range(200):
        s = "".join(rng.choice("ab") for _ in range(rng.randint(0, 9)))
        assert is_palindrome(s) is (s == s[::-1]), f"{s!r}"
