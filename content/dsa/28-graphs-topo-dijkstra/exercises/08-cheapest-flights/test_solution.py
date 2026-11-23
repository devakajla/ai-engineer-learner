import random
from solution import cheapest_price


def brute(n, flights, src, dst, k):
    best = [None]

    def go(node, cost, flights_used):
        if node == dst:
            if best[0] is None or cost < best[0]:
                best[0] = cost
        if flights_used == k + 1:
            return
        for u, v, p in flights:
            if u == node:
                go(v, cost + p, flights_used + 1)

    go(src, 0, 0)
    return -1 if best[0] is None else best[0]


def test_examples():
    assert cheapest_price(3, [[0, 1, 100], [1, 2, 100], [0, 2, 500]], 0, 2, 1) == 200
    assert cheapest_price(3, [[0, 1, 100], [1, 2, 100], [0, 2, 500]], 0, 2, 0) == 500


def test_edges():
    assert cheapest_price(2, [], 0, 1, 3) == -1
    assert cheapest_price(2, [[0, 1, 5]], 0, 0, 0) == 0


def test_random():
    rng = random.Random(8)
    for _ in range(200):
        n = rng.randint(2, 5)
        flights = [[a, b, rng.randint(1, 9)] for a in range(n) for b in range(n) if a != b and rng.random() < 0.4]
        src, dst = rng.sample(range(n), 2)
        k = rng.randint(0, 3)
        assert cheapest_price(n, flights, src, dst, k) == brute(n, flights, src, dst, k), f"{n}, {flights}, {src}, {dst}, {k}"
