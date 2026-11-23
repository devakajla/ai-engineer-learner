# Build a tool schema

Write `make_tool(name, description, params)`. It returns the dictionary that describes a tool to the model.

`params` is a dictionary `{parameter_name: (type, description)}`.

The result must look like this:

```python
{
    "type": "function",
    "function": {
        "name": name,
        "description": description,
        "parameters": {
            "type": "object",
            "properties": {
                "<param>": {"type": <type>, "description": <description>},
                ...
            },
            "required": [<all param names, in order>],
        },
    },
}
```

```python
make_tool("add", "Add two numbers.", {"a": ("number", "First"), "b": ("number", "Second")})
# -> {'type': 'function', 'function': {'name': 'add', 'description': 'Add two numbers.',
#     'parameters': {'type': 'object',
#                    'properties': {'a': {'type': 'number', 'description': 'First'},
#                                   'b': {'type': 'number', 'description': 'Second'}},
#                    'required': ['a', 'b']}}}

make_tool("ping", "Check the service.", {})
# properties is {} and required is []
```
