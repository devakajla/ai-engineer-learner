# Manage the memory

Join the two ideas of this lesson. Write `manage_memory(client, history, keep_last, max_tokens)`. It summarizes **only when needed**, then makes sure the result fits the budget.

`estimate_tokens`, `trim_to_budget` and `summarize_old` are in the starter. Use them.

Rules:
1. Count the tokens of the whole history: the sum of `estimate_tokens(message["content"])`.
2. If the total is `<= max_tokens`, return `list(history)` (a copy). Do **not** call the model. A summary costs a call, so do not make one when it is not needed.
3. Otherwise make a shorter history with `summarize_old(client, history, keep_last)`, then return `trim_to_budget(shorter, max_tokens)`.

```python
# 4 short messages, big budget -> nothing happens, no model call
manage_memory(client, history, keep_last=2, max_tokens=1000)   # -> a copy of history

# long history, small budget -> summary message + recent messages, trimmed to fit
manage_memory(client, long_history, keep_last=2, max_tokens=60)
```

**Think first:** why check the size *before* calling the model?
