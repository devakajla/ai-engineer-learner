import random
from itertools import permutations
from solution import longest_palindrome


def brute(s):
    best = 0
    for size in range(len(s), 0, -1):
        for p in set(permutations(s, size)):
            if list(p) == list(reversed(p)):
                return size
    return best


def test_examples():
    assert longest_palindrome("abccccdd") == 7
    assert longest_palindrome("a") == 1


def test_edges():
    assert longest_palindrome("") == 0
    assert longest_palindrome("Aa") == 1, "case matters"
    assert longest_palindrome("aaaa") == 4
    assert longest_palindrome("abc") == 1


def test_random():
    rng = random.Random(4)
    for _ in range(80):
        s = "".join(rng.choice("abcd") for _ in range(rng.randint(0, 7)))
        assert longest_palindrome(s) == brute(s), f"{s!r}"
