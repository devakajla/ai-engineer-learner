from solution import square


def test_examples():
    assert square(3) == ["***", "***", "***"]
    assert square(1) == ["*"]


def test_more():
    assert square(0) == []
    assert square(4) == ["****"] * 4
