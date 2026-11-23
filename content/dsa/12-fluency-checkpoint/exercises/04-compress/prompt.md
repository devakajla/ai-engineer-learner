# Compress a string

Write `compress(s)` that replaces each run of the same character by the character and the run length. Always write the count, even for 1.

```python
compress("aaabbc")   # -> "a3b2c1"
compress("abc")      # -> "a1b1c1"
compress("")         # -> ""
```

**Think first:** walk the string and keep the "current character" and "how many in a row".

**Hint:** when the character changes, write the finished run and restart the count; remember the last run after the loop.
