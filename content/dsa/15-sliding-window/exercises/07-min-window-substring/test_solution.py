import random
from solution import min_window


def has_all(part, t):
    return all(part.count(c) >= t.count(c) for c in set(t))


def brute(s, t):
    for length in range(len(t), len(s) + 1):
        for i in range(len(s) - length + 1):
            if has_all(s[i:i + length], t):
                return s[i:i + length]
    return ""


def test_examples():
    assert min_window("ADOBECODEBANC", "ABC") == "BANC"
    assert min_window("a", "aa") == ""


def test_edges():
    assert min_window("a", "a") == "a"
    assert min_window("abc", "") == ""
    assert min_window("", "a") == ""
    assert min_window("aab", "ab") == "ab", "leftmost shortest, not the first window found"
    assert min_window("bba", "ab") == "ba"


def test_random():
    rng = random.Random(7)
    for _ in range(300):
        s = "".join(rng.choice("abc") for _ in range(rng.randint(0, 12)))
        t = "".join(rng.choice("abc") for _ in range(rng.randint(1, 4)))
        assert min_window(s, t) == brute(s, t), f"{s!r}, {t!r}"
