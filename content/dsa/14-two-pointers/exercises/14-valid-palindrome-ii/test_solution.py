import random
from solution import valid_palindrome_ii


def brute(s):
    if s == s[::-1]:
        return True
    return any((s[:i] + s[i + 1:]) == (s[:i] + s[i + 1:])[::-1] for i in range(len(s)))


def test_examples():
    assert valid_palindrome_ii("abca") is True
    assert valid_palindrome_ii("abc") is False


def test_edges():
    assert valid_palindrome_ii("") is True
    assert valid_palindrome_ii("a") is True
    assert valid_palindrome_ii("ab") is True, "delete one letter"
    assert valid_palindrome_ii("aba") is True
    assert valid_palindrome_ii("deeee") is True
    assert valid_palindrome_ii("abcdba") is True, "delete c"
    assert valid_palindrome_ii("abcdeba") is False, "needs two deletions"


def test_random():
    rng = random.Random(12)
    for _ in range(400):
        s = "".join(rng.choice("abc") for _ in range(rng.randint(0, 9)))
        assert valid_palindrome_ii(s) is brute(s), f"{s!r}"
