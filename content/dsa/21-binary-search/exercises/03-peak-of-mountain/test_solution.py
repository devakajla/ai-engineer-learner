import random
from solution import peak_index


def test_examples():
    assert peak_index([0, 2, 5, 3, 1]) == 2
    assert peak_index([1, 3, 2]) == 1


def test_edges():
    assert peak_index([0, 10, 5, 2]) == 1
    assert peak_index([3, 5, 7, 9, 4]) == 3
    assert peak_index([1, 2, 3, 4, 3, 2, 1]) == 3


def test_random():
    rng = random.Random(3)
    for _ in range(300):
        up = rng.randint(1, 8)
        down = rng.randint(1, 8)
        values = rng.sample(range(100), up + down + 1)
        top = max(values)
        values.remove(top)
        left = sorted(values[:up])
        right = sorted(values[up:], reverse=True)
        arr = left + [top] + right
        assert peak_index(arr) == up, f"{arr}"
