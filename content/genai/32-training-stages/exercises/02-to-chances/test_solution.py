from solution import to_chances


def test_example():
    result = to_chances({"the": {"cat": 2}, "cat": {"sat": 1, "ran": 3}})
    assert result == {"the": {"cat": 1.0}, "cat": {"sat": 0.25, "ran": 0.75}}


def test_empty():
    assert to_chances({}) == {}


def test_rounding():
    result = to_chances({"a": {"x": 1, "y": 1, "z": 1}})
    assert result == {"a": {"x": 0.33, "y": 0.33, "z": 0.33}}, "round to 2 places"


def test_input_not_changed():
    counts = {"a": {"b": 2, "c": 2}}
    to_chances(counts)
    assert counts == {"a": {"b": 2, "c": 2}}, "do not change the dictionary that was passed in"


def test_keeps_order():
    result = to_chances({"a": {"z": 1, "b": 3}})
    assert list(result["a"]) == ["z", "b"], "keep the order of the next words"
