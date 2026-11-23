import random
from solution import longest_mountain


def is_mountain(p):
    if len(p) < 3:
        return False
    i = 0
    while i + 1 < len(p) and p[i + 1] > p[i]:
        i += 1
    if i == 0 or i == len(p) - 1:
        return False
    while i + 1 < len(p) and p[i + 1] < p[i]:
        i += 1
    return i == len(p) - 1


def brute(arr):
    best = 0
    for i in range(len(arr)):
        for j in range(i + 2, len(arr)):
            if is_mountain(arr[i:j + 1]):
                best = max(best, j - i + 1)
    return best


def test_examples():
    assert longest_mountain([2, 1, 4, 7, 3, 2, 5]) == 5
    assert longest_mountain([2, 2, 2]) == 0


def test_edges():
    assert longest_mountain([]) == 0
    assert longest_mountain([0, 1, 0]) == 3
    assert longest_mountain([1, 2, 3]) == 0, "no down part"
    assert longest_mountain([3, 2, 1]) == 0, "no up part"


def test_random():
    rng = random.Random(14)
    for _ in range(400):
        arr = [rng.randint(0, 4) for _ in range(rng.randint(0, 10))]
        assert longest_mountain(arr) == brute(arr), f"{arr}"
