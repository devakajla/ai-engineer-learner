import random
from solution import can_attend_all


def brute(m):
    return not any(a[0] < b[1] and b[0] < a[1] for i, a in enumerate(m) for b in m[i + 1:])


def test_examples():
    assert can_attend_all([[0, 30], [5, 10], [15, 20]]) is False
    assert can_attend_all([[7, 10], [2, 4]]) is True


def test_edges():
    assert can_attend_all([]) is True
    assert can_attend_all([[1, 5]]) is True
    assert can_attend_all([[1, 5], [5, 8]]) is True, "touching is fine"
    assert can_attend_all([[1, 10], [2, 3]]) is False, "one inside another"


def test_random():
    rng = random.Random(4)
    for _ in range(300):
        m = []
        for _ in range(rng.randint(0, 5)):
            s = rng.randint(0, 12)
            m.append([s, s + rng.randint(1, 4)])
        assert can_attend_all(m) is brute(m), f"{m}"
