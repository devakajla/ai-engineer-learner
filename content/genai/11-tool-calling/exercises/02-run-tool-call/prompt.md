# Run one tool call

Write `run_tool_call(call, functions)`. It runs the function that the model asked for, and returns the `tool` message to send back.

`call` is a tool call. It has `call.id`, `call.function.name` and `call.function.arguments` (a JSON string).
`functions` is a dictionary `{name: python function}`.

Rules:
- Return `{"role": "tool", "tool_call_id": call.id, "content": <text>}`.
- Parse the arguments with `json.loads` and call the function with `**args`. The content is `str(result)`.
- If the name is not in `functions`, the content is `"error: unknown tool <name>"`.
- If the arguments are not valid JSON, the content is `"error: invalid arguments"`.
- If the function raises any exception, the content is `"error: <the exception message>"`.

```python
def add(a, b):
    return a + b

run_tool_call(call, {"add": add})
# call: add with '{"a": 2, "b": 3}'  -> {'role': 'tool', 'tool_call_id': 'c1', 'content': '5'}
```
