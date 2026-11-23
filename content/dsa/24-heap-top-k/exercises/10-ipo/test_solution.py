import random
from solution import max_capital


def brute(k, w, profits, capital, used=0):
    if k == 0:
        return w
    best = w
    for i in range(len(profits)):
        if not used & (1 << i) and capital[i] <= w:
            best = max(best, brute(k - 1, w + profits[i], profits, capital, used | (1 << i)))
    return best


def test_examples():
    assert max_capital(2, 0, [1, 2, 3], [0, 1, 1]) == 4
    assert max_capital(3, 0, [1, 2, 3], [0, 1, 2]) == 6


def test_edges():
    assert max_capital(5, 0, [1], [5]) == 0, "cannot afford anything"
    assert max_capital(0, 3, [1], [0]) == 3


def test_random():
    rng = random.Random(10)
    for _ in range(200):
        n = rng.randint(0, 6)
        profits = [rng.randint(0, 5) for _ in range(n)]
        capital = [rng.randint(0, 6) for _ in range(n)]
        k = rng.randint(0, 4)
        w = rng.randint(0, 3)
        assert max_capital(k, w, profits, capital) == brute(k, w, profits, capital), f"{k}, {w}, {profits}, {capital}"
