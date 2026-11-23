# Add a turn to the history

Write `add_turn(history, role, content)`. It returns a **new** list: the old history plus one new message.

Rules:
- The new message is a dictionary `{"role": role, "content": content}`. It goes at the end.
- Do **not** change the list that was passed in.

```python
h = [{"role": "user", "content": "Hi"}]

add_turn(h, "assistant", "Hello!")
# -> [{'role': 'user', 'content': 'Hi'}, {'role': 'assistant', 'content': 'Hello!'}]

len(h)   # -> 1   (the original list is unchanged)
```
