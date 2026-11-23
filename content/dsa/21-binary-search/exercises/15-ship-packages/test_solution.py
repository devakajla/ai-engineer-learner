import random
from solution import ship_capacity


def days_needed(weights, cap):
    count, load = 1, 0
    for w in weights:
        if load + w > cap:
            count, load = count + 1, w
        else:
            load += w
    return count


def brute(weights, days):
    cap = max(weights)
    while days_needed(weights, cap) > days:
        cap += 1
    return cap


def test_examples():
    assert ship_capacity([1, 2, 3, 4, 5, 6, 7, 8, 9, 10], 5) == 15
    assert ship_capacity([3, 2, 2, 4, 1, 4], 3) == 6


def test_edges():
    assert ship_capacity([5], 1) == 5
    assert ship_capacity([1, 2, 3], 3) == 3
    assert ship_capacity([1, 2, 3], 1) == 6


def test_random():
    rng = random.Random(15)
    for _ in range(300):
        weights = [rng.randint(1, 12) for _ in range(rng.randint(1, 8))]
        days = rng.randint(1, len(weights))
        assert ship_capacity(weights, days) == brute(weights, days), f"{weights}, {days}"
