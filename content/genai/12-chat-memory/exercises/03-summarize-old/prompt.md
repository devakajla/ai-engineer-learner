# Summarize the old part of a chat

Write `summarize_old(client, history, keep_last)`. It replaces the old messages by a short summary from the model, and keeps the last `keep_last` messages as they are.

Rules:
- If `len(history) <= keep_last`, return a copy of the history (`list(history)`). Do **not** call the model.
- Otherwise, compute `cut = len(history) - keep_last`. The old messages are `history[:cut]`, the recent messages are `history[cut:]`.
- Make a transcript of the old messages: one line per message, `"<role>: <content>"`, joined with `"\n"`.
- Call `client.chat.completions.create(model="qwen/qwen3.8-27b", messages=messages, temperature=0)` with one `user` message whose content is `"Summarize this conversation in 2 sentences:\n" + transcript`.
- The summary is `response.choices[0].message.content`.
- Return `[{"role": "user", "content": "Summary of the earlier chat: " + summary}] + recent`.

```python
h = [m1, m2, m3, m4, m5]
summarize_old(client, h, 2)
# -> [summary message, m4, m5]      (m1, m2, m3 were summarized)

summarize_old(client, h, 0)
# -> [summary message]              (everything was summarized)

summarize_old(client, h, 9)
# -> a copy of h, and no model call
```
