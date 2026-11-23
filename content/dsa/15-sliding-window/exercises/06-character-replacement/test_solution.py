import random
from solution import character_replacement


def brute(s, k):
    best = 0
    for i in range(len(s)):
        for j in range(i, len(s)):
            part = s[i:j + 1]
            if len(part) - max(part.count(c) for c in set(part)) <= k:
                best = max(best, len(part))
    return best


def test_examples():
    assert character_replacement("AABABBA", 1) == 4
    assert character_replacement("ABAB", 2) == 4


def test_edges():
    assert character_replacement("", 3) == 0
    assert character_replacement("AAAA", 0) == 4
    assert character_replacement("ABCD", 0) == 1
    assert character_replacement("ABCD", 10) == 4, "k bigger than the string"


def test_random():
    rng = random.Random(6)
    for _ in range(300):
        s = "".join(rng.choice("ABC") for _ in range(rng.randint(0, 12)))
        k = rng.randint(0, 4)
        assert character_replacement(s, k) == brute(s, k), f"{s!r}, {k}"
