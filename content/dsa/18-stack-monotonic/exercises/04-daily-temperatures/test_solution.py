import random
from solution import daily_temperatures


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
    assert daily_temperatures([73, 74, 75, 71, 69, 72, 76, 73]) == [1, 1, 4, 2, 1, 1, 0, 0]
    assert daily_temperatures([30, 20, 10]) == [0, 0, 0]


def test_edges():
    assert daily_temperatures([]) == []
    assert daily_temperatures([50]) == [0]
    assert daily_temperatures([10, 20, 30]) == [1, 1, 0]


def test_random():
    rng = random.Random(4)
    for _ in range(300):
        t = [rng.randint(30, 40) for _ in range(rng.randint(0, 12))]
        assert daily_temperatures(t) == brute(t), f"{t}"
