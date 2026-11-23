from solution import right_triangle


def test_examples():
    assert right_triangle(3) == ["*", "**", "***"]


def test_more():
    assert right_triangle(0) == []
    assert right_triangle(1) == ["*"]
    assert right_triangle(5)[-1] == "*****"
