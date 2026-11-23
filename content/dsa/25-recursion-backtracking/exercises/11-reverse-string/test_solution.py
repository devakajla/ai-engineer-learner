import random
from solution import reverse


def test_examples():
    assert reverse("abc") == "cba"
    assert reverse("") == ""


def test_random():
    rng = random.Random(11)
    for _ in range(100):
        s = "".join(rng.choice("abcxyz") for _ in range(rng.randint(0, 20)))
        assert reverse(s) == s[::-1], f"{s!r}"
