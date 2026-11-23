import random
from solution import search_insert


def test_examples():
    assert search_insert([1, 3, 5, 6], 5) == 2
    assert search_insert([1, 3, 5, 6], 2) == 1


def test_edges():
    assert search_insert([], 4) == 0
    assert search_insert([1, 3, 5, 6], 7) == 4, "after the last item"
    assert search_insert([1, 3, 5, 6], 0) == 0, "before the first item"
    assert search_insert([2], 2) == 0


def test_random():
    rng = random.Random(12)
    for _ in range(300):
        nums = sorted(rng.sample(range(-15, 15), rng.randint(0, 10)))
        t = rng.randint(-17, 17)
        assert search_insert(nums, t) == sum(1 for x in nums if x < t), f"{nums}, {t}"
