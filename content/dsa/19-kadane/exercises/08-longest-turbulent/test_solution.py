import random
from solution import longest_turbulent


def turbulent(part):
    signs = []
    for a, b in zip(part, part[1:]):
        signs.append(1 if b > a else -1 if b < a else 0)
    return all(s != 0 for s in signs) and all(signs[i] == -signs[i + 1] for i in range(len(signs) - 1))


def brute(arr):
    best = 0
    for i in range(len(arr)):
        for j in range(i, len(arr)):
            if turbulent(arr[i:j + 1]):
                best = max(best, j - i + 1)
    return best


def test_examples():
    assert longest_turbulent([9, 4, 2, 10, 7, 8, 8, 1, 9]) == 5
    assert longest_turbulent([4, 8, 12, 16]) == 2


def test_edges():
    assert longest_turbulent([]) == 0
    assert longest_turbulent([100]) == 1
    assert longest_turbulent([9, 9]) == 1
    assert longest_turbulent([1, 2, 1, 2, 1]) == 5


def test_random():
    rng = random.Random(8)
    for _ in range(300):
        arr = [rng.randint(0, 4) for _ in range(rng.randint(0, 10))]
        assert longest_turbulent(arr) == brute(arr), f"{arr}"
