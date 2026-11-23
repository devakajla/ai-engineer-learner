import random
from collections import Counter
from solution import top_k_frequent


def test_examples():
    assert top_k_frequent([1, 1, 1, 2, 2, 3], 2) == [1, 2]
    assert top_k_frequent([4, 4, 5, 5, 6], 2) == [4, 5]


def test_edges():
    assert top_k_frequent([9], 1) == [9]
    assert top_k_frequent([3, 1, 2], 3) == [1, 2, 3]


def test_random():
    rng = random.Random(4)
    for _ in range(200):
        v = [rng.randint(0, 6) for _ in range(rng.randint(1, 15))]
        c = Counter(v)
        k = rng.randint(1, len(c))
        want = [x for x, _ in sorted(c.items(), key=lambda p: (-p[1], p[0]))][:k]
        assert top_k_frequent(v, k) == want, f"{v}, {k}"
