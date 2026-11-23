from solution import invert


def test_examples():
    assert invert({"a": 1, "b": 2}) == {1: "a", 2: "b"}
    assert invert({}) == {}


def test_more():
    original = {"x": "y"}
    assert invert(original) == {"y": "x"}
    assert original == {"x": "y"}, "do not change the input"
    assert invert({1: (1, 2)}) == {(1, 2): 1}
