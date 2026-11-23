from solution import pyramid


def test_examples():
    assert pyramid(3) == ["  *", " ***", "*****"]


def test_more():
    assert pyramid(1) == ["*"]
    assert pyramid(0) == []
    assert pyramid(4) == ["   *", "  ***", " *****", "*******"]
