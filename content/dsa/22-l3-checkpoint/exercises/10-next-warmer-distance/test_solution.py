import random
from solution import days_until_warmer


def brute(t):
    out = []
    for i in range(len(t)):
        d = 0
        for j in range(i + 1, len(t)):
            if t[j] > t[i]:
                d = j - i
                break
        out.append(d)
    return out


def test_examples():
    assert days_until_warmer([73, 74, 75, 71, 69, 72, 76, 73]) == [1, 1, 4, 2, 1, 1, 0, 0]
    assert days_until_warmer([30, 20, 10]) == [0, 0, 0]


def test_edges():
    assert days_until_warmer([]) == []
    assert days_until_warmer([5]) == [0]
    assert days_until_warmer([5, 5, 5]) == [0, 0, 0]


def test_random():
    rng = random.Random(10)
    for _ in range(300):
        t = [rng.randint(0, 9) for _ in range(rng.randint(0, 10))]
        assert days_until_warmer(t) == brute(t), f"{t}"
