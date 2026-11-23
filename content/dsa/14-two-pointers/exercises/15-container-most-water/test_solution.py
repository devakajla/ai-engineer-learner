import random
from solution import max_water


def brute(h):
    return max((min(h[i], h[j]) * (j - i) for i in range(len(h)) for j in range(i + 1, len(h))), default=0)


def test_examples():
    assert max_water([1, 8, 6, 2, 5, 4, 8, 3, 7]) == 49
    assert max_water([1, 1]) == 1


def test_edges():
    assert max_water([]) == 0
    assert max_water([5]) == 0
    assert max_water([0, 0]) == 0
    assert max_water([4, 3, 2, 1, 4]) == 16
    assert max_water([1, 2, 1]) == 2


def test_random():
    rng = random.Random(13)
    for _ in range(300):
        h = [rng.randint(0, 12) for _ in range(rng.randint(0, 10))]
        assert max_water(h) == brute(h), f"{h}"


def test_big_input_is_fast():
    h = [(i * 37) % 1000 for i in range(100000)]
    max_water(h)
