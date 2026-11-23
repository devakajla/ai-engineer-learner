import random
from solution import car_pooling


def brute(trips, capacity):
    points = {s for _, s, _ in trips}
    for p in points:
        if sum(n for n, s, e in trips if s <= p < e) > capacity:
            return False
    return True


def test_examples():
    assert car_pooling([[2, 1, 5], [3, 3, 7]], 4) is False
    assert car_pooling([[2, 1, 5], [3, 3, 7]], 5) is True


def test_edges():
    assert car_pooling([], 1) is True
    assert car_pooling([[3, 2, 4], [3, 4, 6]], 3) is True, "people leave before others get in"
    assert car_pooling([[5, 0, 1]], 4) is False


def test_random():
    rng = random.Random(14)
    for _ in range(300):
        trips = []
        for _ in range(rng.randint(0, 5)):
            s = rng.randint(0, 6)
            trips.append([rng.randint(1, 4), s, rng.randint(s + 1, 8)])
        cap = rng.randint(1, 8)
        assert car_pooling(trips, cap) is brute(trips, cap), f"{trips}, {cap}"
