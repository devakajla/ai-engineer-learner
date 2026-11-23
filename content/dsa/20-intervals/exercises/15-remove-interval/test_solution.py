import random
from solution import remove_interval


def brute(iv, rem):
    pts = sorted({t for a, b in iv for t in range(a, b) if not (rem[0] <= t < rem[1])})
    out = []
    for t in pts:
        # merge only if the same original interval contains both t-1 and t
        same = out and out[-1][1] == t and any(a <= t - 1 and t < b for a, b in iv)
        if same:
            out[-1][1] = t + 1
        else:
            out.append([t, t + 1])
    return out


def test_examples():
    assert remove_interval([[0, 2], [3, 4], [5, 7]], [1, 6]) == [[0, 1], [6, 7]]
    assert remove_interval([[0, 5]], [2, 3]) == [[0, 2], [3, 5]]


def test_edges():
    assert remove_interval([], [1, 2]) == []
    assert remove_interval([[1, 3]], [5, 6]) == [[1, 3]]
    assert remove_interval([[1, 3]], [0, 10]) == []
    assert remove_interval([[0, 2], [2, 4]], [1, 3]) == [[0, 1], [3, 4]]


def test_random():
    rng = random.Random(15)
    for _ in range(300):
        cur, iv = 0, []
        for _ in range(rng.randint(0, 4)):
            s = cur + rng.randint(1, 3)
            e = s + rng.randint(1, 4)
            iv.append([s, e])
            cur = e
        x = rng.randint(0, 15)
        rem = [x, x + rng.randint(1, 6)]
        got = remove_interval([list(i) for i in iv], list(rem))
        want = brute(iv, rem)
        assert got == want, f"{iv}, {rem}: got {got}, want {want}"
