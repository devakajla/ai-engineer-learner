# Longest common prefix

Write `common_prefix(words)` that returns the longest prefix shared by all words. Return `""` if there is none or the list is empty.

```python
common_prefix(["flower", "flow", "flight"])   # -> "fl"
common_prefix(["dog", "car"])                 # -> ""
common_prefix(["same"])                       # -> "same"
```

**Think first:** compare the words character by character at position 0, 1, 2 ... until they differ.

**Hint:** use the first word as the reference; stop at the first mismatch or when a word is too short.
