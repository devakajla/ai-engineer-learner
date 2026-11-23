# Count substrings with at most k distinct characters

Write `count_at_most_k_distinct(s, k)` that returns **how many substrings** of `s` have at most `k` different characters. Substrings at different positions count separately. `k >= 1`.

```python
count_at_most_k_distinct("aab", 1)    # -> 4   ("a", "a", "aa", "b")
count_at_most_k_distinct("abc", 2)    # -> 5   ("a", "b", "c", "ab", "bc")
```

**Think first:** when the window `[lo..hi]` is valid, every start from `lo` to `hi` gives a valid substring ending at `hi`. How many is that?

**Hint:** pattern *variable window, count*: same as exercise 03, but add `hi - lo + 1` to a total at every step. (This "at most" counter is a building block for "exactly k" questions.)
