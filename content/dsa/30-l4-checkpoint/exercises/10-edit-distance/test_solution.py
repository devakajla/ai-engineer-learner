import random
from solution import edit_distance


def brute(a, b):
    if not a:
        return len(b)
    if not b:
        return len(a)
    if a[-1] == b[-1]:
        return brute(a[:-1], b[:-1])
    return 1 + min(brute(a[:-1], b), brute(a, b[:-1]), brute(a[:-1], b[:-1]))


def test_examples():
    assert edit_distance("horse", "ros") == 3
    assert edit_distance("", "abc") == 3


def test_edges():
    assert edit_distance("", "") == 0
    assert edit_distance("same", "same") == 0


def test_random():
    rng = random.Random(10)
    for _ in range(300):
        a = "".join(rng.choice("abc") for _ in range(rng.randint(0, 5)))
        b = "".join(rng.choice("abc") for _ in range(rng.randint(0, 5)))
        assert edit_distance(a, b) == brute(a, b), f"{a!r}, {b!r}"
