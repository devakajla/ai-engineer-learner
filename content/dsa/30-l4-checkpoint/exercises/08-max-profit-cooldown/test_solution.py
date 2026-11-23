import random
from solution import max_profit_cooldown


def brute(prices):
    n = len(prices)

    def go(i, holding, cooldown):
        if i >= n:
            return 0
        best = go(i + 1, holding, False)
        if holding:
            best = max(best, prices[i] + go(i + 1, False, True))
        elif not cooldown:
            best = max(best, -prices[i] + go(i + 1, True, False))
        return best

    return go(0, False, False)


def test_examples():
    assert max_profit_cooldown([1, 2, 3, 0, 2]) == 3
    assert max_profit_cooldown([1]) == 0


def test_edges():
    assert max_profit_cooldown([]) == 0


def test_random():
    rng = random.Random(8)
    for _ in range(300):
        prices = [rng.randint(0, 8) for _ in range(rng.randint(0, 8))]
        assert max_profit_cooldown(list(prices)) == brute(prices), f"{prices}"
