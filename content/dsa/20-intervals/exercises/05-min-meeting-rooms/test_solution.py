import random
from solution import min_meeting_rooms


def brute(m):
    best = 0
    for t in range(0, 20):
        best = max(best, sum(1 for s, e in m if s <= t < e))
    return best


def test_examples():
    assert min_meeting_rooms([[0, 30], [5, 10], [15, 20]]) == 2
    assert min_meeting_rooms([[7, 10], [2, 4]]) == 1


def test_edges():
    assert min_meeting_rooms([]) == 0
    assert min_meeting_rooms([[1, 5], [5, 9]]) == 1, "room is free at the end time"
    assert min_meeting_rooms([[1, 5], [1, 5], [1, 5]]) == 3


def test_random():
    rng = random.Random(5)
    for _ in range(300):
        m = []
        for _ in range(rng.randint(0, 7)):
            s = rng.randint(0, 12)
            m.append([s, s + rng.randint(1, 5)])
        assert min_meeting_rooms(m) == brute(m), f"{m}"
