# Stop a looping agent

Agents can get stuck: the model asks for the **same tool call** again and again. Waiting for `max_steps` wastes money. Stop early.

In the starter: `run_tool_call`, `message_to_dict` and `agent_step`. Write `run_agent_safe(client, question, tools, functions, system="You are a helpful assistant.", max_steps=5, max_repeats=2)`. It works like `run_agent` (exercise 3: same messages, same steps, same `done` and `max_steps` results) and adds a loop check.

Loop check:
- A call is "the same" when its tool name **and** its arguments text are equal. (Use a key like `name + "|" + arguments`.)
- Count how many times each call has been asked for, over the whole run.
- When a call is asked for **more than `max_repeats` times**, stop at once. Return `{"answer": None, "steps": step, "stopped": "loop", "messages": messages}`. The tool results of that step are already in `messages`.
- Different arguments are a different call.

Hint: after each step, look at the messages that were **added** in that step. The assistant message has a `"tool_calls"` list of dictionaries (see `message_to_dict`).

```python
# the model asks for add with {"a": 1} three times in a row, max_repeats=2
run_agent_safe(client, "q", tools, functions)
# -> {'answer': None, 'steps': 3, 'stopped': 'loop', 'messages': [...]}
```
