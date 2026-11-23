from solution import invert_dict


def test_examples():
    assert invert_dict({"a": 1, "b": 2}) == {1: "a", 2: "b"}
    assert invert_dict({}) == {}


def test_more():
    assert invert_dict({1: "x"}) == {"x": 1}
    d = {"a": 1}
    invert_dict(d)
    assert d == {"a": 1}, "do not change the input"
