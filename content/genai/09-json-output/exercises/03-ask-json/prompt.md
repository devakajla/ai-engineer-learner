# Ask for JSON

Write `ask_json(client, question)`. It asks the model for a JSON reply and returns the data.

Your `parse_json` function from the first exercise is **given** in `starter.py`. Use it. Do not change it.

Rules:
- Send two messages. First a `system` message with exactly `"Reply with JSON only."`. Then a `user` message with the `question`.
- Call `client.chat.completions.create(model="qwen/qwen3.8-27b", messages=messages, response_format={"type": "json_object"}, temperature=0)`.
- Take `response.choices[0].message.content` and parse it with `json.loads`.
- If it is not valid JSON, return `None`.

```python
ask_json(client, "Give name and age of Dev, 30")
# model says '{"name": "Dev", "age": 30}'  -> {'name': 'Dev', 'age': 30}

ask_json(client, "Hi")
# model says 'Hello!'                      -> None
```
