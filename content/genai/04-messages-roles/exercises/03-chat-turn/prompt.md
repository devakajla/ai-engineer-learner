# One turn of a chat

Write `chat_turn(client, history, question, model="qwen/qwen3.8-27b")`. It sends the history plus a new question, and returns the reply and the new history.

Your `add_turn` function from the previous exercise is **given** in `starter.py`. Use it. Do not change it.

Rules:
- `history` is a list of `user` and `assistant` messages (no system message).
- Messages to send = the history plus one new `user` message with the `question`.
- Call `client.chat.completions.create(model=model, messages=messages)`.
- The reply text is `response.choices[0].message.content`.
- Return a tuple `(reply, new_history)`. `new_history` is the old history plus the user message plus the assistant reply.
- Do **not** change the `history` that was passed in.

**Think first:** Which list do you send to the model, and which list do you return?

**Hint:** Call `add_turn` twice.

```python
reply, h = chat_turn(client, [], "Hi")
# reply    -> 'Hello!'
# h        -> [{'role': 'user', 'content': 'Hi'}, {'role': 'assistant', 'content': 'Hello!'}]

reply, h = chat_turn(client, h, "Thanks")
# the model gets 3 messages: Hi, Hello!, Thanks
```
