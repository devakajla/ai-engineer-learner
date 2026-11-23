import random
from solution import coin_ways


def brute(coins, amount):
    def go(left, start):
        if left == 0:
            return 1
        return sum(go(left - coins[i], i) for i in range(start, len(coins)) if coins[i] <= left)

    return go(amount, 0)


def test_examples():
    assert coin_ways([1, 2, 5], 5) == 4
    assert coin_ways([2], 3) == 0


def test_edges():
    assert coin_ways([3], 0) == 1
    assert coin_ways([], 0) == 1


def test_random():
    rng = random.Random(11)
    for _ in range(200):
        coins = sorted(rng.sample(range(1, 8), rng.randint(1, 3)))
        amount = rng.randint(0, 14)
        assert coin_ways(list(coins), amount) == brute(coins, amount), f"{coins}, {amount}"
