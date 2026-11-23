# Compress a long chat

A chat grows with every turn, and so does the token bill. The model also gets worse when the context is stuffed with old text (GenAI lesson 24, "lost in the middle"). A good trick: **keep the last few messages word for word and replace everything older with a short summary**.

The starter gives you `ask(client, prompt, system=None, temperature=0)` (one model call, returns the stripped text). Write `compress_history(client, messages, keep_last=4)`. `messages` is a list of `{"role": ..., "content": ...}` dicts.

1. If `len(messages) <= keep_last`: return `messages` unchanged and make **no** model call.
2. Otherwise split into `older` (everything except the last `keep_last` messages) and `recent` (the last `keep_last`; with `keep_last=0` it is empty).
3. Build a transcript: one line per older message, `"<role>: <content>"`, joined with `"\n"`.
4. `summary = ask(client, "Summarise this chat in 2 short sentences. Keep names and decisions.\n\n" + transcript)`.
5. Return `[{"role": "system", "content": "Summary of the earlier chat: " + summary}] + recent`.

```python
compress_history(client, chat_of_8, keep_last=3)
# -> [{'role': 'system', 'content': 'Summary of the earlier chat: ...'}, m5, m6, m7]
```

**Think first:** what can go wrong if the summary leaves out a name or a decision?

**Hint:** `messages[:-keep_last]` breaks when `keep_last` is 0 (it gives an empty list), so handle 0 on its own.
