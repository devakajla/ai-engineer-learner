from solution import diamond


def test_examples():
    assert diamond(3) == ["  *", " ***", "*****", " ***", "  *"]


def test_more():
    assert diamond(1) == ["*"]
    assert diamond(2) == [" *", "***", " *"]
    assert len(diamond(5)) == 9
    assert diamond(4)[3] == "*******"
