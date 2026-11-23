# Longest substring without repeating characters

Write `longest_unique(s)` that returns the length of the longest substring of `s` in which **no character appears twice**.

```python
longest_unique("abcabcbb")    # -> 3   ("abc")
longest_unique("bbbb")        # -> 1
```

**Think first:** when the new character already sits inside the window, how far left must you move `lo` so the window is valid again?

**Hint:** pattern *variable window, maximum*: keep a counter-dict (or a set) of the window; `while counts[ch] > 1:` shrink from the left.
