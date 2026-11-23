# Validate tool arguments

The model sends tool arguments as a JSON string. Never trust them. Write `validate_tool_args(args_json, required)`.

`required` is a list of the argument names that must be present.

Return a tuple `(ok, result)`:
- If the text is not valid JSON: `(False, "invalid JSON")`.
- If it is valid JSON but not an object (a dictionary): `(False, "arguments must be an object")`.
- If some required names are missing: `(False, "missing: <names joined with ', '>")`. Keep the order of `required`.
- Otherwise: `(True, args)` where `args` is the parsed dictionary.
- Extra keys are allowed.

```python
validate_tool_args('{"city": "Delhi"}', ["city"])      # -> (True, {'city': 'Delhi'})
validate_tool_args("nope", ["city"])                   # -> (False, 'invalid JSON')
validate_tool_args("[1, 2]", ["city"])                 # -> (False, 'arguments must be an object')
validate_tool_args('{"a": 1}', ["a", "b", "c"])        # -> (False, 'missing: b, c')
```
