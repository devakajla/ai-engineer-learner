import random
from solution import max_vowels


def brute(s, k):
    return max(sum(1 for c in s[i:i + k] if c in "aeiou") for i in range(len(s) - k + 1))


def test_examples():
    assert max_vowels("abciiidef", 3) == 3
    assert max_vowels("leetcode", 3) == 2


def test_edges():
    assert max_vowels("rhythms", 4) == 0
    assert max_vowels("aeiou", 5) == 5
    assert max_vowels("b", 1) == 0


def test_random():
    rng = random.Random(15)
    for _ in range(300):
        s = "".join(rng.choice("abcdeiou") for _ in range(rng.randint(1, 14)))
        k = rng.randint(1, len(s))
        assert max_vowels(s, k) == brute(s, k), f"{s!r}, {k}"
