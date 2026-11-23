# Longest substring with at most k distinct characters

Write `longest_k_distinct(s, k)` that returns the length of the longest substring of `s` that has **at most `k` different characters**. `k >= 1`.

```python
longest_k_distinct("eceba", 2)    # -> 3   ("ece")
longest_k_distinct("aa", 1)       # -> 2
```

**Think first:** what do you store about the window so you know how many different characters it has? What happens when a character's count drops to 0?

**Hint:** pattern *variable window, maximum* with a counter-dict: `while len(counts) > k:` shrink. Delete a key when its count reaches 0.
