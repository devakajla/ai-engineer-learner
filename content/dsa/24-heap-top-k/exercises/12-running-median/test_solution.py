import random
from solution import running_medians


def brute(nums):
    out = []
    for i in range(1, len(nums) + 1):
        s = sorted(nums[:i])
        m = len(s) // 2
        out.append(s[m] if len(s) % 2 else (s[m - 1] + s[m]) / 2)
    return out


def test_examples():
    assert running_medians([5, 15, 1, 3]) == [5, 10.0, 5, 4.0]
    assert running_medians([2]) == [2]


def test_edges():
    assert running_medians([]) == []
    assert running_medians([1, 1, 1]) == [1, 1.0, 1]


def test_random():
    rng = random.Random(12)
    for _ in range(200):
        v = [rng.randint(-9, 9) for _ in range(rng.randint(0, 12))]
        assert running_medians(v) == brute(v), f"{v}"
