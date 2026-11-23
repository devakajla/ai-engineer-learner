import random
from solution import merge_intervals


def brute(intervals):
    points = set()
    for s, e in intervals:
        points.update(range(s * 2, e * 2 + 1))   # doubled so touching intervals share a point
    out, run = [], []
    for p in sorted(points):
        if run and p != run[-1] + 1:
            out.append([run[0] // 2, run[-1] // 2])
            run = []
        run.append(p)
    if run:
        out.append([run[0] // 2, run[-1] // 2])
    return out


def test_examples():
    assert merge_intervals([[1, 3], [2, 6], [8, 10], [15, 18]]) == [[1, 6], [8, 10], [15, 18]]
    assert merge_intervals([[1, 4], [4, 5]]) == [[1, 5]]


def test_edges():
    assert merge_intervals([]) == []
    assert merge_intervals([[5, 7]]) == [[5, 7]]
    assert merge_intervals([[1, 10], [2, 3], [4, 5]]) == [[1, 10]], "inside another interval"
    assert merge_intervals([[3, 4], [1, 2]]) == [[1, 2], [3, 4]], "unsorted input"


def test_random():
    rng = random.Random(1)
    for _ in range(300):
        ivs = []
        for _ in range(rng.randint(0, 6)):
            s = rng.randint(0, 10)
            ivs.append([s, s + rng.randint(0, 4)])
        assert merge_intervals([list(i) for i in ivs]) == brute(ivs), f"{ivs}"
