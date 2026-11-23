import random
from solution import is_anagram


def test_examples():
    assert is_anagram("anagram", "nagaram") is True
    assert is_anagram("rat", "car") is False


def test_edges():
    assert is_anagram("", "") is True
    assert is_anagram("a", "ab") is False
    assert is_anagram("aab", "abb") is False


def test_random():
    rng = random.Random(6)
    for _ in range(300):
        s = "".join(rng.choice("abc") for _ in range(rng.randint(0, 6)))
        t = "".join(rng.choice("abc") for _ in range(rng.randint(0, 6)))
        assert is_anagram(s, t) is (sorted(s) == sorted(t)), f"{s!r}, {t!r}"
