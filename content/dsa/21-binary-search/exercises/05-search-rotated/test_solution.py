import random
from solution import search_rotated


def test_examples():
    assert search_rotated([4, 5, 6, 7, 0, 1, 2], 0) == 4
    assert search_rotated([4, 5, 6, 7, 0, 1, 2], 3) == -1


def test_edges():
    assert search_rotated([], 1) == -1
    assert search_rotated([1], 1) == 0
    assert search_rotated([1], 0) == -1
    assert search_rotated([3, 1], 1) == 1
    assert search_rotated([1, 3], 3) == 1


def test_random():
    rng = random.Random(5)
    for _ in range(500):
        base = sorted(rng.sample(range(-20, 20), rng.randint(1, 12)))
        k = rng.randint(0, len(base) - 1)
        nums = base[k:] + base[:k]
        t = rng.randint(-22, 22)
        want = nums.index(t) if t in nums else -1
        assert search_rotated(nums, t) == want, f"{nums}, {t}"
