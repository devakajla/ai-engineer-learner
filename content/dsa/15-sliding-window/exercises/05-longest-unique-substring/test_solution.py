import random
from solution import longest_unique


def brute(s):
    best = 0
    for i in range(len(s)):
        for j in range(i, len(s)):
            if len(set(s[i:j + 1])) == j - i + 1:
                best = max(best, j - i + 1)
    return best


def test_examples():
    assert longest_unique("abcabcbb") == 3
    assert longest_unique("bbbb") == 1


def test_edges():
    assert longest_unique("") == 0
    assert longest_unique("pwwkew") == 3
    assert longest_unique("abba") == 2, "lo must never move backwards"
    assert longest_unique("dvdf") == 3


def test_random():
    rng = random.Random(5)
    for _ in range(300):
        s = "".join(rng.choice("abcde") for _ in range(rng.randint(0, 14)))
        assert longest_unique(s) == brute(s), f"{s!r}"
