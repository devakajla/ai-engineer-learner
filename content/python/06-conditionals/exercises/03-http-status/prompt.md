# HTTP status text

Write `status_text(code)` using `match` that returns:

- `200` → `"OK"`
- `201` → `"Created"`
- `400` or `422` → `"Client error"`
- `404` → `"Not found"`
- any other code from 500 to 599 → `"Server error"`
- anything else → `"Unknown"`

```python
status_text(404)   # -> "Not found"
status_text(503)   # -> "Server error"
status_text(302)   # -> "Unknown"
```

Hint: a `case x if 500 <= x <= 599:` guard handles the range.
