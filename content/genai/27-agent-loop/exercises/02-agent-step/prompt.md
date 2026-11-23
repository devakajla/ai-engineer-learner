# One step of the agent

In the starter: `run_tool_call` (lesson 11) and `message_to_dict` (exercise 1). `import json` is there too.

One **step** = one call to the model, plus running the tools it asked for. Write `agent_step(client, messages, tools, functions)`.

Rules:
1. Call `client.chat.completions.create(model="qwen/qwen3.8-27b", messages=messages, tools=tools)`. Take `message = response.choices[0].message`.
2. Make a **new** list: `messages` plus `message_to_dict(message)`. Never change the list you were given.
3. If `message.tool_calls` is empty or `None`, the agent is **done**. Return `{"done": True, "answer": message.content, "messages": new_messages}`.
4. Otherwise run **every** call with `run_tool_call(call, functions)` and add each result message (in order) to the new list. Return `{"done": False, "answer": None, "messages": new_messages}`.

```python
# the model asks for get_weather:
agent_step(client, messages, tools, functions)
# -> {'done': False, 'answer': None, 'messages': [... old messages, assistant message, tool message]}
```

**Think first:** why does the model need to see its own tool request in the next call?
