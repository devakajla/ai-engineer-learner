# Ask with settings

Write `ask_with(client, question, temperature=0.7, max_output_tokens=500, stop=None)`. It asks the model one question with settings, and returns the answer text.

Your `build_messages` function from lesson 4 is **given** in `starter.py`. Use it for the messages. Do not change it.

Rules:
- Use model `"qwen/qwen3.8-27b"`.
- `messages` is one user message with the `question`.
- Send `temperature=temperature` and `max_completion_tokens=max_output_tokens`.
- Only send `stop` if it is not `None`.
- Return `response.choices[0].message.content`.

```python
ask_with(client, "Name a colour.", temperature=0, max_output_tokens=5)
# calls create(model=..., messages=[...], temperature=0, max_completion_tokens=5)

ask_with(client, "List 3 fruits.", stop="END")
# also sends stop="END"
```
