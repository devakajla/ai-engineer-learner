import random
from solution import max_points


def brute(cards, k):
    n = len(cards)
    return max(sum(cards[:i]) + sum(cards[n - (k - i):]) for i in range(k + 1))


def test_examples():
    assert max_points([1, 2, 3, 4, 5, 6, 1], 3) == 12
    assert max_points([2, 2, 2], 2) == 4


def test_edges():
    assert max_points([5], 1) == 5
    assert max_points([1, 2, 3], 3) == 6, "take all cards"
    assert max_points([9, 7, 7, 9, 7, 7, 9], 7) == 55


def test_random():
    rng = random.Random(18)
    for _ in range(300):
        n = rng.randint(1, 10)
        cards = [rng.randint(0, 9) for _ in range(n)]
        k = rng.randint(1, n)
        assert max_points(cards, k) == brute(cards, k), f"{cards}, {k}"
