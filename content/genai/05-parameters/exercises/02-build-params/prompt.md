# Settings by task

Write `build_params(task)`. It returns the settings dictionary for a kind of task.

| task | temperature | max_completion_tokens |
| --- | --- | --- |
| `"extract"` | `0` | `200` |
| `"chat"` | `0.7` | `500` |
| `"creative"` | `1.0` | `800` |

Rules:
- Return a dictionary with exactly the keys `"temperature"` and `"max_completion_tokens"`.
- For any other task name, raise `ValueError` with the message `"unknown task: <name>"`.

```python
build_params("extract")
# -> {'temperature': 0, 'max_completion_tokens': 200}

build_params("poem")
# raises ValueError: unknown task: poem
```
