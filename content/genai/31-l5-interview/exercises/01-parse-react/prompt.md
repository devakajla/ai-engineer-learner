# Parse a ReAct reply

Before native tool calling, agents used a **text format** called ReAct. The model writes lines like:

```
Thought: I need the weather.
Action: get_weather
Action Input: {"city": "Delhi"}
```

or, when it is done:

```
Thought: I know the answer.
Final Answer: It is sunny.
```

Write `parse_react(text)`. `import json` is in the starter. Return one of:

- `{"type": "final", "answer": ...}`: the first line that starts with `Final Answer:` (after removing spaces at the start of the line) comes **before** any `Action:` line, or there is no action. The answer is the text after `Final Answer:` **plus any lines that follow**, stripped of spaces at both ends.
- `{"type": "action", "tool": name, "args": dict}`: there is an `Action:` line (the name after the colon, stripped). Then the first `Action Input:` line **after it** holds JSON. If there is no `Action Input:` line, `args` is `{}`.
- `{"type": "error", "reason": "no action"}`: no `Final Answer:` and no `Action:` line, or the action name is empty.
- `{"type": "error", "reason": "bad arguments"}`: the `Action Input:` text is not valid JSON, or is JSON but not an object (a dictionary).

If both markers exist, the one that comes **first** wins.

```python
parse_react('Thought: x\nAction: add\nAction Input: {"a": 1, "b": 2}')
# -> {'type': 'action', 'tool': 'add', 'args': {'a': 1, 'b': 2}}
parse_react("Thought: done\nFinal Answer: 42")
# -> {'type': 'final', 'answer': '42'}
parse_react("Thought: hmm")
# -> {'type': 'error', 'reason': 'no action'}
```

**Think first:** why do models and APIs now prefer native tool calls over this text format?
