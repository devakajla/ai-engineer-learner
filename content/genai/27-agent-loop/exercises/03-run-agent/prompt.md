# The agent loop

Now the loop. In the starter: `run_tool_call`, `message_to_dict` and `agent_step`.

Write `run_agent(client, question, tools, functions, system="You are a helpful assistant.", max_steps=5)`.

Rules:
1. Start with two messages: the system message and the user message (the question).
2. Repeat up to `max_steps` times: run `agent_step`. Keep the new messages it returns.
3. When a step says `done`, return `{"answer": answer, "steps": n, "stopped": "done", "messages": messages}`. `n` counts from 1.
4. If you used all steps and the model is still asking for tools, return `{"answer": None, "steps": max_steps, "stopped": "max_steps", "messages": messages}`.

```python
# step 1: model calls add. step 2: model answers "The sum is 3."
run_agent(client, "1 + 2?", tools, functions)
# -> {'answer': 'The sum is 3.', 'steps': 2, 'stopped': 'done', 'messages': [...5 messages...]}
```

**Think first:** what would happen without `max_steps` if the model never stops asking for tools?
