import random
from collections import Counter
from solution import frequency_sort


def test_examples():
    assert frequency_sort("tree") == "eert"
    assert frequency_sort("cccaaa") == "aaaccc"


def test_edges():
    assert frequency_sort("") == ""
    assert frequency_sort("a") == "a"


def test_random():
    rng = random.Random(7)
    for _ in range(200):
        s = "".join(rng.choice("abcde") for _ in range(rng.randint(0, 12)))
        c = Counter(s)
        want = "".join(ch * n for ch, n in sorted(c.items(), key=lambda p: (-p[1], p[0])))
        assert frequency_sort(s) == want, f"{s!r}"
