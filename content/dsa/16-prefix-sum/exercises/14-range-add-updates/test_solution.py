import random
from solution import apply_updates


def test_examples():
    assert apply_updates(5, [[1, 3, 2], [2, 4, 3], [0, 2, -2]]) == [-2, 0, 3, 5, 3]
    assert apply_updates(3, []) == [0, 0, 0]


def test_edges():
    assert apply_updates(1, [[0, 0, 5]]) == [5]
    assert apply_updates(3, [[0, 2, 1], [0, 2, 1]]) == [2, 2, 2]


def test_random():
    rng = random.Random(13)
    for _ in range(200):
        n = rng.randint(1, 10)
        ups = []
        want = [0] * n
        for _ in range(rng.randint(0, 6)):
            l = rng.randint(0, n - 1)
            r = rng.randint(l, n - 1)
            v = rng.randint(-5, 5)
            ups.append([l, r, v])
            for i in range(l, r + 1):
                want[i] += v
        assert apply_updates(n, ups) == want, f"{n}, {ups}"
