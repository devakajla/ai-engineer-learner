# Estimate tokens

Write `estimate_tokens(text)`. Use the rule: 1 token is about 4 characters. Divide the number of characters by 4 and **round up**.

Rules:
- Return a whole number (an `int`).
- An empty string gives `0`.
- Do not import anything. Use `//`.

```python
estimate_tokens("hello world")   # -> 3      (11 characters)
estimate_tokens("abcd")          # -> 1
estimate_tokens("")              # -> 0
```
