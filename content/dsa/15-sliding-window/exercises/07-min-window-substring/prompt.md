# Minimum window substring

Write `min_window(s, t)` that returns the **shortest substring of `s` that contains every character of `t`** (with repeats: if `t` has two `"a"`, the window needs two `"a"`). Return `""` if there is none. If two answers have the same length, return the **leftmost**.

```python
min_window("ADOBECODEBANC", "ABC")    # -> "BANC"
min_window("a", "aa")                 # -> ""
```

**Think first:** how can you know in O(1) whether the window already has everything it needs? (Count how many letters are still missing.)

**Hint:** pattern *variable window, minimum*: expand `hi` until valid, then `while valid:` record the best and shrink `lo`. Keep a `need` dict and a `missing` number.
