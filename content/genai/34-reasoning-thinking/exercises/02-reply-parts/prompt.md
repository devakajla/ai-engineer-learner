# Handle both reply shapes

Some settings put the thinking in a separate field (`message.reasoning`). Others leave it inside `message.content` in `<think>` tags. Your code should handle both.

Your `split_thinking(text)` from the previous exercise is **given** in `starter.py`. Do not change it.

Write `reply_parts(message)`. `message` has `message.content` (text or `None`) and maybe `message.reasoning` (text or `None`; the attribute may be missing).

Return a dictionary `{"thinking": ..., "answer": ...}`.

Rules:
- If `message.reasoning` exists and is not empty, then `thinking` is that text (stripped) and `answer` is `message.content` (stripped).
- Otherwise use `split_thinking(message.content)`.
- If `content` is `None`, treat it as `""`.

**Think first:** Which shape do you check for first, and what is the fallback?

**Hint:** `getattr(message, "reasoning", None)` reads an attribute that may not exist.

```python
reply_parts(NS(content="14 apples", reasoning="23-9=14 ..."))
# -> {'thinking': '23-9=14 ...', 'answer': '14 apples'}

reply_parts(NS(content="<think>x</think>14 apples"))
# -> {'thinking': 'x', 'answer': '14 apples'}
```
