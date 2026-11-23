from solution import make_tool


def test_two_params():
    assert make_tool("add", "Add two numbers.", {"a": ("number", "First"), "b": ("number", "Second")}) == {
        "type": "function",
        "function": {
            "name": "add",
            "description": "Add two numbers.",
            "parameters": {
                "type": "object",
                "properties": {
                    "a": {"type": "number", "description": "First"},
                    "b": {"type": "number", "description": "Second"},
                },
                "required": ["a", "b"],
            },
        },
    }


def test_no_params():
    tool = make_tool("ping", "Check the service.", {})
    assert tool["function"]["parameters"] == {"type": "object", "properties": {}, "required": []}


def test_required_keeps_order():
    tool = make_tool("f", "d", {"z": ("string", "Z"), "a": ("integer", "A")})
    assert tool["function"]["parameters"]["required"] == ["z", "a"]
    assert tool["function"]["parameters"]["properties"]["a"]["type"] == "integer"
