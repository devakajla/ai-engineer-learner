# One round of tool calling

Write `chat_with_tools(client, messages, tools, functions)`. It does one full round of tool calling and returns the final text.

The helper `run_tool_call(call, functions)` from the last exercise is already in the starter. Use it.

Rules:
1. Call `client.chat.completions.create(model="qwen/qwen3.8-27b", messages=messages, tools=tools)`.
2. Let `message = response.choices[0].message`. If `message.tool_calls` is empty or `None`, return `message.content`.
3. Otherwise make the assistant message:
   `{"role": "assistant", "content": message.content, "tool_calls": [{"id": c.id, "type": "function", "function": {"name": c.function.name, "arguments": c.function.arguments}} for each call c]}`
4. Run every tool call with `run_tool_call` to get the tool messages.
5. Call the model again with `messages + [assistant message] + tool messages` (a new list, the same `tools`). Return `response.choices[0].message.content` of this second call.
- Do not change the `messages` list that was passed in.

```python
chat_with_tools(client, [{"role": "user", "content": "What is 2+3?"}], tools, {"add": add})
# 1st call: the model asks for add(a=2, b=3)
# your code runs it -> '5'
# 2nd call: messages now hold the tool result; the model says 'It is 5.'
# -> 'It is 5.'
```
