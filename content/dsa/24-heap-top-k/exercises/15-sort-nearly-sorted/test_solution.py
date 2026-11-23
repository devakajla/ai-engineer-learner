import random
from solution import sort_nearly_sorted


def test_examples():
    assert sort_nearly_sorted([2, 1, 4, 3, 6, 5], 1) == [1, 2, 3, 4, 5, 6]
    assert sort_nearly_sorted([3, 2, 1], 2) == [1, 2, 3]


def test_edges():
    assert sort_nearly_sorted([], 3) == []
    assert sort_nearly_sorted([1, 2, 3], 0) == [1, 2, 3]


def test_random():
    rng = random.Random(15)
    for _ in range(200):
        v = sorted(rng.randint(0, 20) for _ in range(rng.randint(0, 12)))
        k = rng.randint(0, 4)
        shuffled = list(v)
        for i in range(len(shuffled)):
            j = min(len(shuffled) - 1, i + rng.randint(0, k))
            shuffled[i], shuffled[j] = shuffled[j], shuffled[i]
        far = max((abs(i - v.index(x)) for i, x in enumerate(shuffled)), default=0)
        kk = max(k * 2, far)
        assert sort_nearly_sorted(list(shuffled), kk) == v, f"{shuffled}, {kk}"
