# How much of the output was thinking?

Thinking costs output tokens. Work out what share of the output was thinking.

Your `estimate_tokens(text)` from lesson 2 is **given** in `starter.py`. Do not change it.

Write `thinking_share(thinking, output_tokens)`:
- `thinking_tokens` is `estimate_tokens(thinking)`.
- Return `thinking_tokens / output_tokens`, rounded to 2 decimal places.
- If `output_tokens` is `0`, return `0.0`.
- The share can never be more than `1.0`. If the estimate is larger than `output_tokens`, return `1.0`.

**Think first:** What two edge cases must you check before you divide?

**Hint:** `min(...)` keeps the value at or below 1.

```python
thinking_share("a" * 400, 200)   # -> 0.5     (100 of 200 tokens)
thinking_share("", 50)           # -> 0.0
thinking_share("a" * 4000, 100)  # -> 1.0
thinking_share("abc", 0)         # -> 0.0
```
