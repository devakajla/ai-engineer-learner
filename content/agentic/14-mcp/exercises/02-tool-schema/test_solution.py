import pytest

from solution import result_text, to_input_schema, to_openai_tool


def test_schema_for_two_params():
    assert to_input_schema({"a": "int", "name": "str"}) == {
        "type": "object",
        "properties": {"a": {"type": "integer"}, "name": {"type": "string"}},
        "required": ["a", "name"],
    }


def test_all_supported_types():
    schema = to_input_schema({"i": "int", "s": "str", "f": "float", "b": "bool"})
    assert [p["type"] for p in schema["properties"].values()] == ["integer", "string", "number", "boolean"]


def test_no_params():
    assert to_input_schema({}) == {"type": "object", "properties": {}, "required": []}


def test_unknown_type_raises():
    with pytest.raises(ValueError, match="unknown type: list"):
        to_input_schema({"x": "list"})


def test_mcp_tool_becomes_an_openai_style_tool():
    tool = {"name": "add", "description": "Add numbers.", "inputSchema": to_input_schema({"a": "int"})}
    assert to_openai_tool(tool) == {
        "type": "function",
        "function": {"name": "add", "description": "Add numbers.", "parameters": tool["inputSchema"]},
    }


def test_result_text_joins_text_items_and_skips_others():
    result = {"content": [{"type": "text", "text": "one"}, {"type": "image", "data": "..."}, {"type": "text", "text": "two"}]}
    assert result_text(result) == "one\ntwo"
    assert result_text({"content": []}) == ""
    assert result_text({}) == ""
