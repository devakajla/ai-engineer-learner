import random
from solution import kth_missing


def brute(arr, k):
    present = set(arr)
    n = 0
    while True:
        n += 1
        if n not in present:
            k -= 1
            if k == 0:
                return n


def test_examples():
    assert kth_missing([2, 3, 4, 7, 11], 5) == 9
    assert kth_missing([1, 2, 3, 4], 2) == 6


def test_edges():
    assert kth_missing([], 3) == 3
    assert kth_missing([5], 1) == 1
    assert kth_missing([5], 5) == 6


def test_random():
    rng = random.Random(19)
    for _ in range(400):
        arr = sorted(rng.sample(range(1, 25), rng.randint(0, 10)))
        k = rng.randint(1, 15)
        assert kth_missing(arr, k) == brute(arr, k), f"{arr}, {k}"
