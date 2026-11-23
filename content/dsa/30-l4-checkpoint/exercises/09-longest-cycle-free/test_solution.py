import random
from solution import largest_group


def brute(n, friends):
    label = list(range(n))
    changed = True
    while changed:
        changed = False
        for a, b in friends:
            m = min(label[a], label[b])
            if label[a] != m or label[b] != m:
                label[a] = label[b] = m
                changed = True
    return max((label.count(x) for x in set(label)), default=0)


def test_examples():
    assert largest_group(5, [[0, 1], [1, 2], [3, 4]]) == 3
    assert largest_group(3, []) == 1


def test_edges():
    assert largest_group(0, []) == 0


def test_random():
    rng = random.Random(9)
    for _ in range(300):
        n = rng.randint(0, 8)
        friends = [[a, b] for a in range(n) for b in range(a + 1, n) if rng.random() < 0.2]
        assert largest_group(n, friends) == brute(n, friends), f"{n}, {friends}"
