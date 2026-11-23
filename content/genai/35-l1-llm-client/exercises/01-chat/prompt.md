# One turn of chat, with settings, history and retries

Put your Level 1 pieces together. The helpers `build_params`, `add_turn` and `backoff_delays` (and a few more) are **given** in `starter.py`. Do not change them.

Write `chat(client, history, question, task="chat", max_tries=3, sleep=None)`. It returns a tuple `(reply, new_history)`.

Rules:
- Get the settings with `build_params(task)`. An unknown task raises `ValueError("unknown task: <name>")` **before** any call is made.
- If `max_tries` is less than `1`, raise `ValueError("max_tries must be at least 1")`.
- The messages to send are the history plus one new `user` message (use `add_turn`).
- Call `client.chat.completions.create(model="qwen/qwen3.8-27b", messages=messages, **params)`.
- If the call raises an exception, try again, up to `max_tries` calls in total. If all fail, raise the **last** exception.
- If `sleep` is not `None`, call `sleep(delay)` after each failed try **except the last one**. The delays are `backoff_delays(max_tries - 1)`.
- On success, the reply is `response.choices[0].message.content`. The new history is the messages plus one `assistant` message with the reply.
- Never change the `history` that was passed in.

**Think first:** In which order do you check the task, the tries and the call? What do you return on success?

**Hint:** The `final_price` example in the lesson: call the pieces in the right order.

```python
reply, h = chat(client, [], "Hi")
# sends temperature=0.7 and max_completion_tokens=500 (the "chat" settings)
# reply -> 'Hello!'
# h     -> [{'role': 'user', 'content': 'Hi'}, {'role': 'assistant', 'content': 'Hello!'}]

chat(client, [], "Hi", task="poem")   # raises ValueError: unknown task: poem
```
