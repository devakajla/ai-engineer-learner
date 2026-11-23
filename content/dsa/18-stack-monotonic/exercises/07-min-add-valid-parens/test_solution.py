import random
from solution import min_add_to_make_valid


def valid(s):
    bal = 0
    for ch in s:
        bal += 1 if ch == "(" else -1
        if bal < 0:
            return False
    return bal == 0


def brute(s):
    # try inserting 0, 1, 2, ... parentheses
    level = {s}
    count = 0
    while True:
        if any(valid(x) for x in level):
            return count
        level = {x[:i] + c + x[i:] for x in level for i in range(len(x) + 1) for c in "()"}
        count += 1


def test_examples():
    assert min_add_to_make_valid("())") == 1
    assert min_add_to_make_valid("(((") == 3


def test_edges():
    assert min_add_to_make_valid("") == 0
    assert min_add_to_make_valid("()") == 0
    assert min_add_to_make_valid(")(") == 2


def test_random():
    rng = random.Random(7)
    for _ in range(80):
        s = "".join(rng.choice("()") for _ in range(rng.randint(0, 6)))
        assert min_add_to_make_valid(s) == brute(s), f"{s!r}"
