import random
from solution import insert_interval


def brute(intervals, new):
    merged = []
    for s, e in sorted(intervals + [new]):
        if merged and s <= merged[-1][1]:
            merged[-1][1] = max(merged[-1][1], e)
        else:
            merged.append([s, e])
    return merged


def test_examples():
    assert insert_interval([[1, 3], [6, 9]], [2, 5]) == [[1, 5], [6, 9]]
    assert insert_interval([[1, 2], [3, 5], [6, 7], [8, 10]], [4, 8]) == [[1, 2], [3, 10]]


def test_edges():
    assert insert_interval([], [5, 7]) == [[5, 7]]
    assert insert_interval([[1, 5]], [2, 3]) == [[1, 5]]
    assert insert_interval([[3, 5]], [0, 1]) == [[0, 1], [3, 5]]
    assert insert_interval([[1, 2]], [5, 6]) == [[1, 2], [5, 6]]
    assert insert_interval([[1, 5]], [5, 8]) == [[1, 8]], "touching merges"


def test_random():
    rng = random.Random(2)
    for _ in range(300):
        cur, ivs = 0, []
        for _ in range(rng.randint(0, 5)):
            s = cur + rng.randint(1, 3)
            e = s + rng.randint(0, 3)
            ivs.append([s, e])
            cur = e
        s = rng.randint(0, 20)
        new = [s, s + rng.randint(0, 6)]
        assert insert_interval([list(i) for i in ivs], list(new)) == brute(ivs, new), f"{ivs}, {new}"
