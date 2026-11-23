import random
from solution import count_occurrences


def test_examples():
    assert count_occurrences([1, 2, 2, 2, 3, 5], 2) == 3
    assert count_occurrences([1, 2, 3], 4) == 0


def test_edges():
    assert count_occurrences([], 1) == 0
    assert count_occurrences([7, 7, 7], 7) == 3
    assert count_occurrences([1, 3], 2) == 0


def test_random():
    rng = random.Random(14)
    for _ in range(300):
        nums = sorted(rng.randint(0, 6) for _ in range(rng.randint(0, 14)))
        t = rng.randint(-1, 7)
        assert count_occurrences(nums, t) == nums.count(t), f"{nums}, {t}"
