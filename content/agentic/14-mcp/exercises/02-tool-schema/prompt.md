# Describe a tool so a model can call it

An MCP server **lists** its tools. Each tool has a `name`, a `description` and an **`inputSchema`** (a JSON Schema that describes the arguments). Your app turns that into the `tools` format the chat API (Groq) expects. When the tool is called, the answer comes back as a list of **content** items (`{"type": "text", "text": "5"}`), and you turn it back into plain text for the model.

Write:

1. `to_input_schema(params)`: `params` maps argument names to simple type names, like `{"a": "int", "name": "str"}`. Use this table (it is given as the dict `TYPES`): `int -> "integer"`, `str -> "string"`, `float -> "number"`, `bool -> "boolean"`. Return `{"type": "object", "properties": {name: {"type": <json type>}, ...}, "required": [all the names, in order]}`. An unknown type name raises `ValueError(f"unknown type: {type_name}")`.
2. `to_openai_tool(tool)`: `tool` is `{"name", "description", "inputSchema"}`. Return `{"type": "function", "function": {"name": ..., "description": ..., "parameters": tool["inputSchema"]}}`.
3. `result_text(result)`: `result` is `{"content": [...], ...}`. Join the `"text"` of every item whose `"type"` is `"text"` with `"\n"`. Skip other types. A missing or empty `content` gives `""`.

```python
to_input_schema({"a": "int", "b": "int"})
# -> {'type': 'object', 'properties': {'a': {'type': 'integer'}, 'b': {'type': 'integer'}}, 'required': ['a', 'b']}
```

**Think first:** the model only ever sees the name, the description and the schema. What does that tell you about how to write a tool description?

**Hint:** `result.get("content", [])` handles a missing key.
