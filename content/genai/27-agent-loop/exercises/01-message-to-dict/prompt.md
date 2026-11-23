# Turn the model's message into a history entry

An agent keeps a list of messages. When the model answers, you must add its message to the list, or on the next call the model will not remember that it asked for a tool.

The SDK gives you an object `message` with `message.content` and `message.tool_calls` (a list, or `None`). Write `message_to_dict(message)`. It returns a plain dictionary:

- Always: `{"role": "assistant", "content": message.content}`.
- If `message.tool_calls` is not empty, also add a key `"tool_calls"`: a list with one dictionary per call, shaped like this:
  `{"id": call.id, "type": "function", "function": {"name": call.function.name, "arguments": call.function.arguments}}`
- If there are no tool calls (`None` or an empty list), do **not** add the key `"tool_calls"` at all.

```python
# a message with no tool calls
message_to_dict(message)   # -> {'role': 'assistant', 'content': 'Hello!'}
# a message that asks for get_weather
message_to_dict(message)
# -> {'role': 'assistant', 'content': None, 'tool_calls': [{'id': 'c1', 'type': 'function',
#     'function': {'name': 'get_weather', 'arguments': '{"city": "Delhi"}'}}]}
```

**Think first:** why must `arguments` stay a text and not become a dictionary?
