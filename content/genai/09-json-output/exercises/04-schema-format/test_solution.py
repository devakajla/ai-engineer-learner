from solution import schema_format


def test_example():
    assert schema_format("person", {"name": "string", "age": "integer"}) == {
        "type": "json_schema",
        "json_schema": {
            "name": "person",
            "schema": {
                "type": "object",
                "properties": {"name": {"type": "string"}, "age": {"type": "integer"}},
                "required": ["name", "age"],
                "additionalProperties": False,
            },
        },
    }


def test_empty_fields():
    schema = schema_format("empty", {})["json_schema"]["schema"]
    assert schema["properties"] == {}
    assert schema["required"] == []


def test_order_and_name():
    result = schema_format("t", {"z": "string", "a": "boolean"})
    assert result["json_schema"]["name"] == "t"
    assert result["json_schema"]["schema"]["required"] == ["z", "a"], "keep the order of the keys"
    assert list(result["json_schema"]["schema"]["properties"]) == ["z", "a"]
