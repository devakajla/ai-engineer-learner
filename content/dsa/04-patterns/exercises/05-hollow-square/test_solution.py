from solution import hollow_square


def test_examples():
    assert hollow_square(4) == ["****", "*  *", "*  *", "****"]
    assert hollow_square(1) == ["*"]


def test_more():
    assert hollow_square(2) == ["**", "**"]
    assert hollow_square(3) == ["***", "* *", "***"]
    assert hollow_square(5)[2] == "*   *"
