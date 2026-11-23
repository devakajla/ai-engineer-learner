import random
from solution import k_smallest_pairs


def brute(a, b, k):
    pairs = sorted(([x, y] for x in a for y in b), key=lambda p: (p[0] + p[1], p[0], p[1]))
    return pairs[:k]


def test_examples():
    assert k_smallest_pairs([1, 7, 11], [2, 4, 6], 3) == [[1, 2], [1, 4], [1, 6]]
    assert k_smallest_pairs([1, 1, 2], [1, 2, 3], 2) == [[1, 1], [1, 1]]


def test_edges():
    assert k_smallest_pairs([], [1], 3) == []
    assert k_smallest_pairs([1], [2], 5) == [[1, 2]]


def test_random():
    rng = random.Random(6)
    for _ in range(200):
        a = sorted(rng.randint(0, 8) for _ in range(rng.randint(0, 5)))
        b = sorted(rng.randint(0, 8) for _ in range(rng.randint(0, 5)))
        k = rng.randint(1, 12)
        assert k_smallest_pairs(a, b, k) == brute(a, b, k), f"{a}, {b}, {k}"
