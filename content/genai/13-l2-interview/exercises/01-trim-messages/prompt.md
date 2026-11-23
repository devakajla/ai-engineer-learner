# Trim messages, keep the system message

Write `trim_messages(messages, max_tokens)`. The list may start with a `system` message. Keep the system message **always**, and then keep the newest other messages that fit in the token budget.

The helper `estimate_tokens(text)` is in the starter (about 1 token per 4 characters, rounded up).

Rules:
- If the first message has role `"system"`, it is always kept. Its tokens **count** against the budget.
- From the other messages, walk from the newest to the oldest. Keep a message if the total so far plus its cost is at most `max_tokens`. **Stop** at the first message that does not fit.
- The result is the system message (if any), then the kept messages in their original order.
- If there is no system message, just trim the messages.
- Do not change the list that was passed in.

```python
m = [
    {"role": "system", "content": "s" * 8},      # 2 tokens
    {"role": "user", "content": "a" * 20},       # 5 tokens
    {"role": "assistant", "content": "b" * 8},   # 2 tokens
    {"role": "user", "content": "c" * 8},        # 2 tokens
]

trim_messages(m, 6)    # -> [system, assistant, user]   (2 + 2 + 2 = 6)
trim_messages(m, 2)    # -> [system]                    (the system message alone fills the budget)
trim_messages(m, 100)  # -> all four messages
```
