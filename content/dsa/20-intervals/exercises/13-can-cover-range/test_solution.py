import random
from solution import can_cover


def brute(iv, lo, hi):
    return all(any(s <= p <= e for s, e in iv) for p in range(lo, hi + 1))


def test_examples():
    assert can_cover([[1, 3], [4, 6]], 1, 6) is True
    assert can_cover([[1, 3], [5, 6]], 1, 6) is False


def test_edges():
    assert can_cover([], 1, 1) is False
    assert can_cover([[0, 10]], 3, 4) is True
    assert can_cover([[2, 5]], 1, 5) is False, "1 is not covered"
    assert can_cover([[1, 2], [2, 5]], 1, 5) is True


def test_random():
    rng = random.Random(13)
    for _ in range(400):
        iv = []
        for _ in range(rng.randint(0, 5)):
            s = rng.randint(0, 10)
            iv.append([s, s + rng.randint(0, 4)])
        lo = rng.randint(0, 5)
        hi = lo + rng.randint(0, 6)
        assert can_cover(iv, lo, hi) is brute(iv, lo, hi), f"{iv}, {lo}, {hi}"
