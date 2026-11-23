# Spot a failing agent

An agent leaves a **trace**: a list of the tool calls it made. Reading traces is how you find out why an agent failed. A program can spot the most common failures for you.

A trace is a list of steps. Each step is a dictionary: `{"tool": name, "args": dict, "result": text}`.

Write `detect_failure(trace, max_steps=10)`. It returns a **list of labels**, in this fixed order (leave out the labels that do not apply; no failure gives `[]`):

1. `"loop"`: some call (same `tool` **and** equal `args`) appears **3 or more times** anywhere in the trace.
2. `"error_streak"`: **3 or more results in a row** start with the text `error`.
3. `"max_steps"`: the trace has `max_steps` steps or more.

```python
t = [{"tool": "search", "args": {"q": "x"}, "result": "nothing"}] * 3
detect_failure(t)                      # -> ['loop']
detect_failure(t, max_steps=3)         # -> ['loop', 'max_steps']
detect_failure([])                     # -> []
```

**Think first:** an agent calls the same tool with the same arguments 3 times. Why is that a sign of trouble, and what can your code do about it?

**Hint:** dictionaries can be compared with `==`. Keep a counter `streak` that goes up on an error result and goes back to 0 otherwise. Do not use `import json`.
