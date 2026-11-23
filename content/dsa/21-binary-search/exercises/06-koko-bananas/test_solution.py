import random
from solution import min_eating_speed


def brute(piles, h):
    k = 1
    while sum((p + k - 1) // k for p in piles) > h:
        k += 1
    return k


def test_examples():
    assert min_eating_speed([3, 6, 7, 11], 8) == 4
    assert min_eating_speed([30, 11, 23, 4, 20], 5) == 30


def test_edges():
    assert min_eating_speed([1], 1) == 1
    assert min_eating_speed([10], 5) == 2
    assert min_eating_speed([1000000000], 2) == 500000000, "must be fast, not a loop over speeds"


def test_random():
    rng = random.Random(6)
    for _ in range(300):
        piles = [rng.randint(1, 30) for _ in range(rng.randint(1, 6))]
        h = rng.randint(len(piles), len(piles) + 12)
        assert min_eating_speed(piles, h) == brute(piles, h), f"{piles}, {h}"
