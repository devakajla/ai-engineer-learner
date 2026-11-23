# Trim to a token budget

Write `trim_to_budget(history, max_tokens)`. It keeps the **newest** messages that fit in the token budget.

`history` is a list of messages like `{"role": "user", "content": "..."}`. The helper `estimate_tokens(text)` is in the starter. It gives about 1 token per 4 characters, rounded up.

Rules:
- Walk from the newest message to the oldest. The cost of a message is `estimate_tokens(message["content"])`.
- Keep a message only if the total so far plus its cost is at most `max_tokens`.
- **Stop** at the first message that does not fit. Do not skip it to keep an older one.
- Return the kept messages in their **original order** (oldest first), as a new list.
- Do not change the list that was passed in.

```python
h = [
    {"role": "user", "content": "a" * 12},        # 3 tokens
    {"role": "assistant", "content": "b" * 16},   # 4 tokens
    {"role": "user", "content": "c" * 8},         # 2 tokens
    {"role": "assistant", "content": "d" * 8},    # 2 tokens
]

trim_to_budget(h, 5)    # -> the last two messages (2 + 2 = 4 tokens)
trim_to_budget(h, 100)  # -> all four messages
trim_to_budget(h, 1)    # -> []   (even the newest costs 2)
```
