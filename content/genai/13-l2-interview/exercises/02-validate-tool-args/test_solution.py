from solution import validate_tool_args


def test_examples():
    assert validate_tool_args('{"city": "Delhi"}', ["city"]) == (True, {"city": "Delhi"})
    assert validate_tool_args("nope", ["city"]) == (False, "invalid JSON")
    assert validate_tool_args("[1, 2]", ["city"]) == (False, "arguments must be an object")
    assert validate_tool_args('{"a": 1}', ["a", "b", "c"]) == (False, "missing: b, c")


def test_edges():
    assert validate_tool_args("{}", []) == (True, {}), "nothing is required"
    assert validate_tool_args('{"a": 1, "extra": 2}', ["a"]) == (True, {"a": 1, "extra": 2}), "extra keys are fine"
    assert validate_tool_args("", ["a"]) == (False, "invalid JSON")
    assert validate_tool_args("5", []) == (False, "arguments must be an object")
    assert validate_tool_args('"text"', []) == (False, "arguments must be an object")
    assert validate_tool_args('{"b": 1}', ["c", "a", "b"]) == (False, "missing: c, a"), "keep the order of required"


def test_a_value_of_null_still_counts_as_present():
    assert validate_tool_args('{"a": null}', ["a"]) == (True, {"a": None})
