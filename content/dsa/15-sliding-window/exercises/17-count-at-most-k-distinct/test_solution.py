import random
from solution import count_at_most_k_distinct


def brute(s, k):
    return sum(1 for i in range(len(s)) for j in range(i, len(s)) if len(set(s[i:j + 1])) <= k)


def test_examples():
    assert count_at_most_k_distinct("aab", 1) == 4
    assert count_at_most_k_distinct("abc", 2) == 5


def test_edges():
    assert count_at_most_k_distinct("", 2) == 0
    assert count_at_most_k_distinct("aaa", 1) == 6
    assert count_at_most_k_distinct("abc", 3) == 6


def test_random():
    rng = random.Random(17)
    for _ in range(300):
        s = "".join(rng.choice("abcd") for _ in range(rng.randint(0, 12)))
        k = rng.randint(1, 4)
        assert count_at_most_k_distinct(s, k) == brute(s, k), f"{s!r}, {k}"
