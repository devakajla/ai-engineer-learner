import random
from solution import is_sorted


def test_examples():
    assert is_sorted([1, 2, 2, 5]) is True
    assert is_sorted([1, 3, 2]) is False


def test_edges():
    assert is_sorted([]) is True
    assert is_sorted([4]) is True


def test_random():
    rng = random.Random(3)
    for _ in range(200):
        v = [rng.randint(0, 4) for _ in range(rng.randint(0, 8))]
        assert is_sorted(v) is (v == sorted(v)), f"{v}"
