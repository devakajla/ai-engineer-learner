# Classify a status code

Write `status_class(code)` that returns which class a status code belongs to:

| Code | Return |
|---|---|
| 100–199 | `"informational"` |
| 200–299 | `"success"` |
| 300–399 | `"redirect"` |
| 400–499 | `"client_error"` |
| 500–599 | `"server_error"` |

For anything outside 100–599, raise `ValueError`.

```python
status_class(201)   # -> "success"
status_class(422)   # -> "client_error"
status_class(503)   # -> "server_error"
status_class(700)   # raises ValueError
```
