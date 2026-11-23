# Check a tool description

The model reads your tool description to decide **when** and **how** to call the tool. A sloppy description gives wrong calls. Write `check_tool_spec(tool)`. It reads a tool dictionary (the shape from GenAI lesson 11) and returns a **list of problem texts**. A good tool gives an empty list `[]`.

`tool` looks like this:

```python
{"type": "function", "function": {
    "name": "get_weather",
    "description": "Get the current weather for a city.",
    "parameters": {"type": "object",
                   "properties": {"city": {"type": "string", "description": "City name"}},
                   "required": ["city"]}}}
```

Check these, in this order. Add **one text per problem** to the list, using exactly these words:

1. The name is empty, or has a character that is not a lowercase letter (`a` to `z`), a digit or `_`: `"name must use lowercase letters, digits and underscores only"`
2. The description (after `strip()`) is shorter than 20 characters: `"description is too short (under 20 characters)"`
3. For each parameter in `properties`, in order:
   - no description, or an empty one: `"parameter <name> has no description"`
   - the `"type"` is not one of `string`, `integer`, `number`, `boolean`, `array`, `object` (or is missing): `"parameter <name> has an unknown type"`
4. For each name in `required`, in order, that is not in `properties`: `"required parameter <name> is not in properties"`

If `parameters`, `properties` or `required` are missing, treat them as empty.

```python
check_tool_spec(good_tool)    # -> []
check_tool_spec({"type": "function", "function": {"name": "GetWeather", "description": "weather"}})
# -> ['name must use lowercase letters, digits and underscores only',
#     'description is too short (under 20 characters)']
```

**Think first:** why does a parameter need a description even when its name looks obvious? What would the model do with a parameter called `q`?

**Hint:** `import string` gives you `string.ascii_lowercase` and `string.digits`. Use `.get(key, default)` so that missing keys do not crash.
