from solution import validate_args

TOOL = {"type": "function", "function": {"name": "t", "description": "d", "parameters": {
    "type": "object",
    "properties": {
        "a": {"type": "integer", "description": "x"},
        "b": {"type": "number", "description": "y"},
        "s": {"type": "string", "description": "z"},
        "f": {"type": "boolean", "description": "w"},
        "l": {"type": "array", "description": "v"},
        "o": {"type": "object", "description": "u"},
    },
    "required": ["a", "s"],
}}}


def test_good_arguments():
    assert validate_args(TOOL, {"a": 1, "s": "x"}) == []
    assert validate_args(TOOL, {"a": 1, "s": "x", "b": 2.5, "f": True, "l": [1], "o": {}}) == []


def test_missing_required_in_order():
    assert validate_args(TOOL, {}) == ["missing required argument a", "missing required argument s"]
    assert validate_args(TOOL, {"s": "x"}) == ["missing required argument a"]


def test_unknown_argument():
    assert validate_args(TOOL, {"a": 1, "s": "x", "zzz": 1}) == ["unknown argument zzz"]


def test_wrong_types():
    assert validate_args(TOOL, {"a": "1", "s": "x"}) == ["argument a must be integer"]
    assert validate_args(TOOL, {"a": 1.5, "s": "x"}) == ["argument a must be integer"]
    assert validate_args(TOOL, {"a": 1, "s": 5}) == ["argument s must be string"]
    assert validate_args(TOOL, {"a": 1, "s": "x", "f": "yes"}) == ["argument f must be boolean"]
    assert validate_args(TOOL, {"a": 1, "s": "x", "l": "abc"}) == ["argument l must be array"]
    assert validate_args(TOOL, {"a": 1, "s": "x", "o": []}) == ["argument o must be object"]


def test_bool_is_not_an_integer_or_a_number():
    assert validate_args(TOOL, {"a": True, "s": "x"}) == ["argument a must be integer"]
    assert validate_args(TOOL, {"a": 1, "s": "x", "b": False}) == ["argument b must be number"]


def test_number_accepts_int_and_float():
    assert validate_args(TOOL, {"a": 1, "s": "x", "b": 3}) == []
    assert validate_args(TOOL, {"a": 1, "s": "x", "b": 3.5}) == []


def test_problems_come_in_order():
    assert validate_args(TOOL, {"zzz": 1, "a": "no"}) == [
        "missing required argument s",
        "unknown argument zzz",
        "argument a must be integer",
    ]


def test_tool_without_parameters():
    tool = {"type": "function", "function": {"name": "ping", "description": "d"}}
    assert validate_args(tool, {}) == []
    assert validate_args(tool, {"x": 1}) == ["unknown argument x"]
