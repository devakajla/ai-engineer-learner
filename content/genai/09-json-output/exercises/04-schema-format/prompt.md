# Build a JSON schema response format

Write `schema_format(name, fields)`. It builds the `response_format` dictionary for JSON schema mode.

`fields` is a dictionary `{key: type name}`, for example `{"name": "string", "age": "integer"}`.

The result must look like this:

```python
{
    "type": "json_schema",
    "json_schema": {
        "name": <name>,
        "schema": {
            "type": "object",
            "properties": {<key>: {"type": <type name>}, ...},
            "required": [<every key, in order>],
            "additionalProperties": False,
        },
    },
}
```

Rules:
- Every key is required.
- Keep the order of the keys.
- Empty `fields` gives empty `properties` and an empty `required` list.

**Think first:** Which part of the result is the same every time, and which part depends on `fields`?

**Hint:** Loop over `fields`, build `properties` and `required` as you go.

```python
schema_format("person", {"name": "string", "age": "integer"})
# -> {'type': 'json_schema', 'json_schema': {'name': 'person', 'schema': {'type': 'object',
#     'properties': {'name': {'type': 'string'}, 'age': {'type': 'integer'}},
#     'required': ['name', 'age'], 'additionalProperties': False}}}
```
