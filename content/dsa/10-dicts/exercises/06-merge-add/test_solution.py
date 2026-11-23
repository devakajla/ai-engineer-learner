from solution import merge_add


def test_examples():
    assert merge_add({"a": 1, "b": 2}, {"b": 3, "c": 4}) == {"a": 1, "b": 5, "c": 4}


def test_more():
    assert merge_add({}, {}) == {}
    assert merge_add({"x": 1}, {}) == {"x": 1}
    assert merge_add({}, {"y": 2}) == {"y": 2}
    a = {"k": 1}
    merge_add(a, {"k": 5})
    assert a == {"k": 1}, "do not change the input"
