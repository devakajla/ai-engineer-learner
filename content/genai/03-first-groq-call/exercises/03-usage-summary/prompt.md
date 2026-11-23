# Summarise token usage

Every response has a `usage` part with token counts. Write `usage_summary(response)` to turn it into a plain dictionary.

Rules:
- Read `response.usage.prompt_tokens`, `response.usage.completion_tokens` and `response.usage.total_tokens`.
- Return a dictionary with the keys `"input"`, `"output"` and `"total"`.

```python
usage_summary(response)
# -> {'input': 12, 'output': 30, 'total': 42}
```
