import random
from solution import is_isomorphic


def pattern(s):
    seen = {}
    return [seen.setdefault(c, len(seen)) for c in s]


def test_examples():
    assert is_isomorphic("egg", "add") is True
    assert is_isomorphic("foo", "bar") is False


def test_edges():
    assert is_isomorphic("", "") is True
    assert is_isomorphic("badc", "baba") is False, "c and a both map to a"
    assert is_isomorphic("paper", "title") is True
    assert is_isomorphic("ab", "aa") is False


def test_random():
    rng = random.Random(8)
    for _ in range(300):
        n = rng.randint(0, 6)
        s = "".join(rng.choice("abc") for _ in range(n))
        t = "".join(rng.choice("xyz") for _ in range(n))
        assert is_isomorphic(s, t) is (pattern(s) == pattern(t)), f"{s!r}, {t!r}"
