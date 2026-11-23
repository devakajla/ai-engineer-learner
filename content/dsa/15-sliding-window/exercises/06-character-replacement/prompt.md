# Longest repeating character replacement

`s` has only uppercase letters. You may change **at most `k`** characters to any letter. Write `character_replacement(s, k)` that returns the length of the longest substring that can become **all the same letter**.

```python
character_replacement("AABABBA", 1)    # -> 4   ("AABA" -> "AAAA")
character_replacement("ABAB", 2)       # -> 4
```

**Think first:** for a window, how many changes do you need? (Think: window length minus the count of the most common letter.)

**Hint:** pattern *variable window, maximum*: window is valid while `length - max(counts.values()) <= k`. Shrink while it is **not** valid.
