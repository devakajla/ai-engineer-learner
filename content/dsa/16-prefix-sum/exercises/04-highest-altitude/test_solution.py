import random
from solution import max_altitude


def test_examples():
    assert max_altitude([-5, 1, 5, 0, -7]) == 1
    assert max_altitude([-4, -3, -2, -1, 4, 3, 2]) == 0


def test_edges():
    assert max_altitude([]) == 0
    assert max_altitude([3, 3]) == 6
    assert max_altitude([-1]) == 0, "the start (0) counts"


def test_random():
    rng = random.Random(3)
    for _ in range(200):
        g = [rng.randint(-5, 5) for _ in range(rng.randint(0, 10))]
        alt = [sum(g[:i]) for i in range(len(g) + 1)]
        assert max_altitude(g) == max(alt), f"{g}"
