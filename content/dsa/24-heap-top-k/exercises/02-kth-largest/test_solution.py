import random
from solution import kth_largest


def test_examples():
    assert kth_largest([3, 2, 1, 5, 6, 4], 2) == 5
    assert kth_largest([3, 2, 3, 1, 2, 4, 5, 5, 6], 4) == 4


def test_edges():
    assert kth_largest([7], 1) == 7
    assert kth_largest([2, 2, 2], 3) == 2


def test_random():
    rng = random.Random(2)
    for _ in range(200):
        v = [rng.randint(-9, 9) for _ in range(rng.randint(1, 12))]
        k = rng.randint(1, len(v))
        assert kth_largest(v, k) == sorted(v, reverse=True)[k - 1], f"{v}, {k}"
