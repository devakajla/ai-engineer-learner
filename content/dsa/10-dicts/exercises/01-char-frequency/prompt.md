# Character frequency

Write `char_frequency(text)` that returns a dict mapping each character to how many times it appears.

```python
char_frequency("aab")    # -> {'a': 2, 'b': 1}
char_frequency("")       # -> {}
```

**Think first:** what is the count for a character you see for the first time?

**Hint:** `counts[ch] = counts.get(ch, 0) + 1`.
