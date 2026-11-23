# Does it fit?

Write `fits(prompt_tokens, max_output, context_limit)`. Return `True` if the input and the longest possible answer both fit in the context window. Otherwise return `False`.

Rules:
- Input tokens plus `max_output` must be less than or equal to `context_limit`.
- Using the whole window exactly is allowed.

```python
fits(1000, 500, 4096)   # -> True
fits(4000, 500, 4096)   # -> False
fits(3596, 500, 4096)   # -> True
```
