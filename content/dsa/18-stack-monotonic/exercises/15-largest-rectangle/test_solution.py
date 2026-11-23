import random
from solution import largest_rectangle


def brute(h):
    best = 0
    for i in range(len(h)):
        low = h[i]
        for j in range(i, len(h)):
            low = min(low, h[j])
            best = max(best, low * (j - i + 1))
    return best


def test_examples():
    assert largest_rectangle([2, 1, 5, 6, 2, 3]) == 10
    assert largest_rectangle([2, 4]) == 4


def test_edges():
    assert largest_rectangle([]) == 0
    assert largest_rectangle([7]) == 7
    assert largest_rectangle([0, 0]) == 0
    assert largest_rectangle([3, 3, 3]) == 9
    assert largest_rectangle([5, 4, 3, 2, 1]) == 9


def test_does_not_change_input():
    h = [2, 1, 5]
    largest_rectangle(h)
    assert h == [2, 1, 5], "do not modify the input list"


def test_random():
    rng = random.Random(15)
    for _ in range(300):
        h = [rng.randint(0, 7) for _ in range(rng.randint(0, 10))]
        assert largest_rectangle(h) == brute(h), f"{h}"
