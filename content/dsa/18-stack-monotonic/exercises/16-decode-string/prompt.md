# Decode a string

The rule is `k[text]`: repeat `text` exactly `k` times. Brackets can be **nested**. Write `decode_string(s)` that returns the decoded string. `k` can have several digits. The input is valid.

```python
decode_string("3[a]2[bc]")        # -> "aaabcbc"
decode_string("3[a2[c]]")         # -> "accaccacc"
```

**Think first:** when you meet `]`, what do you need back: the text built inside the brackets, and the text built before them? And the number?

**Hint:** pattern *stack of (text, count)*: on `[` push `(current_text, number)` and reset; on `]` pop and set `current = previous + current * number`.
