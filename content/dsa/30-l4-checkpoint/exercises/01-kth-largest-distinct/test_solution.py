import random
from solution import kth_largest_distinct


def test_examples():
    assert kth_largest_distinct([3, 1, 3, 2, 2], 2) == 2
    assert kth_largest_distinct([5, 5], 2) is None


def test_random():
    rng = random.Random(1)
    for _ in range(300):
        nums = [rng.randint(0, 6) for _ in range(rng.randint(0, 9))]
        k = rng.randint(1, 5)
        d = sorted(set(nums), reverse=True)
        want = d[k - 1] if len(d) >= k else None
        assert kth_largest_distinct(list(nums), k) == want, f"{nums}, {k}"
