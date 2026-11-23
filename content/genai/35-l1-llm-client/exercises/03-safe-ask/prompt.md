# Ask safely: check first, then call, then report

All your Level 1 pieces are **given** in `starter.py`, including `call_cost` from the previous exercise. Do not change them.

Write `safe_ask(client, question, task, prices, context_limit)`. `prices` is a tuple `(input_price, output_price)`.

Rules:
1. Get the settings with `build_params(task)` (an unknown task raises `ValueError`, as usual).
2. Estimate the tokens of `question`. If the question plus `max_completion_tokens` does **not** fit in `context_limit`, **do not call the model**. Return `{"ok": False, "reason": "too long"}`.
3. Otherwise call `client.chat.completions.create(model="qwen/qwen3.8-27b", messages=..., **params)`. The messages are one `user` message (use `build_messages("", question)`).
4. Return a dictionary: `{"ok": True, "reply": <text>, "usage": ..., "cost": ..., "cut_off": ...}`. The last three come from `call_cost`.

**Think first:** What is the cheapest mistake to avoid, and when do you find out about it?

**Hint:** The answer has three stages: check, call, report.

```python
safe_ask(client, "Hi", "chat", (0.5, 1.5), 4096)
# -> {'ok': True, 'reply': 'Hello!', 'usage': {...}, 'cost': ..., 'cut_off': False}

safe_ask(client, "a" * 20000, "chat", (0.5, 1.5), 4096)
# -> {'ok': False, 'reason': 'too long'}      (and no call is made)
```
