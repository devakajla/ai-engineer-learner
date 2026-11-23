# A ReAct agent in plain text

Here is the whole agent loop, in the **text format** called ReAct (Reason + Act). The model writes `Thought:`, `Action:` and `Action Input:` lines. Your code runs the tool and answers with an `Observation:` line. This continues until the model writes `Final Answer:`.

In the starter you get `parse_react` (from GenAI lesson 31) and `import json`. It turns a reply into `{"type": "final", "answer": ...}`, `{"type": "action", "tool": ..., "args": {...}}` or `{"type": "error", "reason": ...}`.

Write `react_agent(client, question, functions, max_steps=5)`. `functions` is a dictionary `{tool name: python function}`.

1. Start with two messages: a `system` message and a `user` message holding the question. The system message can say anything, but it **must contain every tool name** (the tests check that).
2. Loop for at most `max_steps` model calls. Each call is `client.chat.completions.create(model="qwen/qwen3.8-27b", messages=messages, temperature=0)`. The reply text is `response.choices[0].message.content`.
3. Append the reply to `messages` as an `assistant` message (the exact reply text).
4. Run `parse_react(reply)`:
   - `final`: return `{"answer": the answer, "stopped": "final", "steps": number of model calls so far}`.
   - `error`: the observation is `"error: " + reason`.
   - `action` with a tool that is **not** in `functions`: the observation is `"error: unknown tool <name>"`.
   - `action` with a known tool: the observation is `str(functions[tool](**args))`. If the function raises an exception, it is `"error: <ExceptionClassName>: <message>"`.
5. Append a `user` message `"Observation: " + observation` and go round again.
6. If the loop ends with no final answer, return `{"answer": None, "stopped": "max_steps", "steps": max_steps}`.

```python
# reply 1: 'Thought: add\nAction: add\nAction Input: {"a": 2, "b": 3}'
# reply 2: 'Thought: done\nFinal Answer: 5'
react_agent(client, "What is 2 + 3?", {"add": add})
# -> {'answer': '5', 'stopped': 'final', 'steps': 2}
```

**Think first:** why is the Observation sent as a `user` message and not as a `tool` message here? (Look at what the model writes in this format.)

**Hint:** copy the shape of your agent loop from GenAI lesson 27. A `for step in range(1, max_steps + 1):` loop gives you the step number.
