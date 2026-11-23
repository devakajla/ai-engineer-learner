from solution import number_triangle


def test_examples():
    assert number_triangle(4) == ["1", "12", "123", "1234"]


def test_more():
    assert number_triangle(0) == []
    assert number_triangle(1) == ["1"]
    assert number_triangle(10)[-1] == "12345678910"
