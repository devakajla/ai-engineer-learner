import random
from solution import longest_k_distinct


def brute(s, k):
    best = 0
    for i in range(len(s)):
        for j in range(i, len(s)):
            if len(set(s[i:j + 1])) <= k:
                best = max(best, j - i + 1)
    return best


def test_examples():
    assert longest_k_distinct("eceba", 2) == 3
    assert longest_k_distinct("aa", 1) == 2


def test_edges():
    assert longest_k_distinct("", 2) == 0
    assert longest_k_distinct("abc", 5) == 3, "k bigger than distinct letters"
    assert longest_k_distinct("abcd", 1) == 1


def test_random():
    rng = random.Random(3)
    for _ in range(300):
        s = "".join(rng.choice("abcd") for _ in range(rng.randint(0, 12)))
        k = rng.randint(1, 4)
        assert longest_k_distinct(s, k) == brute(s, k), f"{s!r}, {k}"
