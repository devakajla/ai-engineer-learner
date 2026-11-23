import random
from solution import is_valid


def brute(s):
    while True:
        for pair in ("()", "[]", "{}"):
            if pair in s:
                s = s.replace(pair, "", 1)
                break
        else:
            return s == ""


def test_examples():
    assert is_valid("()[]{}") is True
    assert is_valid("([)]") is False


def test_edges():
    assert is_valid("") is True
    assert is_valid("(") is False
    assert is_valid(")") is False
    assert is_valid("{[]}") is True
    assert is_valid("((") is False, "left over openers"


def test_random():
    rng = random.Random(2)
    for _ in range(400):
        s = "".join(rng.choice("()[]{}") for _ in range(rng.randint(0, 8)))
        assert is_valid(s) is brute(s), f"{s!r}"
