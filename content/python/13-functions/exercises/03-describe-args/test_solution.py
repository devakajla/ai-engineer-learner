from solution import describe


def test_examples():
    assert describe(1, 2, x=5, a=1) == (2, ["a", "x"])
    assert describe() == (0, [])


def test_more():
    assert describe("a", b=1) == (1, ["b"])
    assert describe(*[1, 2, 3], **{"z": 1, "y": 2}) == (3, ["y", "z"])
