import random
from solution import kth_largest_stream


def brute(k, nums):
    return [sorted(nums[:i], reverse=True)[k - 1] if i >= k else None for i in range(1, len(nums) + 1)]


def test_examples():
    assert kth_largest_stream(3, [4, 5, 8, 2, 3]) == [None, None, 4, 4, 4]
    assert kth_largest_stream(1, [5, 3, 7]) == [5, 5, 7]


def test_edges():
    assert kth_largest_stream(2, []) == []
    assert kth_largest_stream(2, [1]) == [None]


def test_random():
    rng = random.Random(16)
    for _ in range(200):
        v = [rng.randint(-9, 9) for _ in range(rng.randint(0, 12))]
        k = rng.randint(1, 5)
        assert kth_largest_stream(k, v) == brute(k, v), f"{k}, {v}"
