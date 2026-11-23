import random
from solution import coin_change


def brute(coins, amount):
    best = [None]

    def go(left, used, start):
        if left == 0:
            if best[0] is None or used < best[0]:
                best[0] = used
            return
        for i in range(start, len(coins)):
            if coins[i] <= left:
                go(left - coins[i], used + 1, i)

    go(amount, 0, 0)
    return -1 if best[0] is None else best[0]


def test_examples():
    assert coin_change([1, 2, 5], 11) == 3
    assert coin_change([2], 3) == -1


def test_edges():
    assert coin_change([1], 0) == 0
    assert coin_change([1, 3, 4], 6) == 2, "greedy gives 3 coins"


def test_random():
    rng = random.Random(10)
    for _ in range(200):
        coins = sorted(rng.sample(range(1, 8), rng.randint(1, 3)))
        amount = rng.randint(0, 14)
        assert coin_change(list(coins), amount) == brute(coins, amount), f"{coins}, {amount}"
