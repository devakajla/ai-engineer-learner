# Parse JSON safely

Write `parse_json(text)`. It turns JSON text into Python data.

Rules:
- If the text is valid JSON, return the data (use `json.loads`).
- If it is not valid JSON, return `None`. Do not raise.

```python
parse_json('{"a": 1}')      # -> {'a': 1}
parse_json('[1, 2, 3]')     # -> [1, 2, 3]
parse_json("hello")         # -> None
parse_json("")              # -> None
```
