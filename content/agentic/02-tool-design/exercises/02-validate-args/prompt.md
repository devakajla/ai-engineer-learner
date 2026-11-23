# Check the arguments a model sends

The model writes the arguments of a tool call. It is a stranger sending you data (GenAI lesson 11). Check the arguments **before** you run the function, and give a clear message when they are wrong.

Write `validate_args(tool, args)`. `tool` has the same shape as in exercise 1. `args` is a dictionary of the arguments the model sent. Return a **list of problem texts**. No problems gives `[]`.

Use exactly these texts, in this order:

1. For each name in `required`, in order, that is not a key of `args`: `"missing required argument <name>"`
2. For each key of `args`, in the order of `args`:
   - it is not in `properties`: `"unknown argument <name>"`
   - its value has the wrong type: `"argument <name> must be <type>"` (the type word from the spec, like `integer`)

Type rules (the starter has `type_ok` for you to write or use as you like):

| spec type | the value must be |
| --- | --- |
| `string` | a `str` |
| `integer` | an `int`, but **not** `True` or `False` |
| `number` | an `int` or a `float`, but not a `bool` |
| `boolean` | a `bool` |
| `array` | a `list` |
| `object` | a `dict` |

```python
tool = {"type": "function", "function": {"name": "add", "description": "...", "parameters": {
    "type": "object",
    "properties": {"a": {"type": "integer", "description": "x"}, "b": {"type": "integer", "description": "y"}},
    "required": ["a", "b"]}}}
validate_args(tool, {"a": 1, "b": 2})                  # -> []
validate_args(tool, {"a": "1", "extra": 5})            # -> ['missing required argument b', 'argument a must be integer', 'unknown argument extra']
```

**Think first:** `True` is an `int` in Python (`isinstance(True, int)` is `True`). Why must a tool that wants an integer refuse `True`?

**Hint:** build the `problems` list and add to it with `append`. Check `isinstance(value, bool)` first when the type is `integer` or `number`.
