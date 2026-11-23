# Rewrite a follow-up question

In a chat, users ask follow-ups: *"And how do I undo it?"* Searching with that text finds nothing, because "it" means nothing alone. Fix: ask the model to rewrite the question so it stands alone.

Write `rewrite_question(client, history, question)`. `history` is a list of chat messages (`role`, `content`).

Rules:
- If `history` is empty, return `question` unchanged and make **no** call.
- Otherwise make a transcript: one line per message, `"<role>: <content>"`, joined with `"\n"`.
- Send one `user` message with exactly this content:
  `"Rewrite the last question so it can be understood without the chat. Reply with the question only.\n\nChat:\n" + transcript + "\n\nLast question: " + question`
- Call with `model="qwen/qwen3.8-27b"`, `temperature=0`, `max_completion_tokens=100`.
- Return the reply text with spaces at the ends removed (`.strip()`).

```python
history = [{"role": "user", "content": "How do I delete a task?"},
           {"role": "assistant", "content": "Use the DELETE endpoint."}]
rewrite_question(client, history, "And how do I undo it?")
# -> 'How do I undo deleting a task?'      (what the model replied)
```
