# Keep the history inside a budget

Agent histories grow with every step (lesson 27). When the history gets too long you must cut it. Write `trim_messages(messages, max_tokens)`.

Token estimate (given in the starter): `estimate_tokens(text) = (len(text) + 3) // 4`. A message with `content` of `None` counts as an empty text.

Rules:
1. If the first message has the role `"system"`, **always keep it**. It counts for the budget.
2. Then add messages from the **newest to the oldest** while the total stays at or under `max_tokens`.
3. Stop at the **first** message (going backwards) that does not fit. Do not skip it to keep an older, smaller one.
4. Return the kept messages in their **original order**. Do not change the input list.
5. If even the system message is bigger than `max_tokens`, still return it (alone).

```python
msgs = [system(8 tokens), user(4), assistant(4), user(4)]
trim_messages(msgs, 16)   # keeps system + the two newest   (8 + 4 + 4)
trim_messages(msgs, 12)   # keeps system + the newest only  (8 + 4)
```

**Think first:** what breaks if you cut a tool message away from the assistant message that asked for it? How would you protect against it?
