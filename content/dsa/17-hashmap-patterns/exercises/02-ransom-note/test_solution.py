import random
from solution import can_construct


def brute(note, magazine):
    return all(note.count(c) <= magazine.count(c) for c in set(note))


def test_examples():
    assert can_construct("aa", "aab") is True
    assert can_construct("aa", "ab") is False


def test_edges():
    assert can_construct("", "") is True
    assert can_construct("", "abc") is True
    assert can_construct("a", "") is False


def test_random():
    rng = random.Random(2)
    for _ in range(300):
        note = "".join(rng.choice("abc") for _ in range(rng.randint(0, 5)))
        mag = "".join(rng.choice("abc") for _ in range(rng.randint(0, 8)))
        assert can_construct(note, mag) is brute(note, mag), f"{note!r}, {mag!r}"
