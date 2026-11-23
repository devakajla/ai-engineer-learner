import random
from solution import is_valid


def brute(s):
    while True:
        t = s.replace("()", "").replace("[]", "").replace("{}", "")
        if t == s:
            return s == ""
        s = t


def test_examples():
    assert is_valid("([]{})") is True
    assert is_valid("(]") is False


def test_edges():
    assert is_valid("") is True
    assert is_valid("(") is False
    assert is_valid(")") is False
    assert is_valid("([)]") is False


def test_random():
    rng = random.Random(4)
    for _ in range(400):
        s = "".join(rng.choice("()[]{}") for _ in range(rng.randint(0, 8)))
        assert is_valid(s) is brute(s), f"{s!r}"
