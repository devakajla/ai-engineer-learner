# Two sum

Write `two_sum(nums, target)` that returns the indexes `[i, j]` (with `i < j`) of two numbers that add up to `target`. Exactly one answer exists.

```python
two_sum([2, 7, 11, 15], 9)   # -> [0, 1]
two_sum([3, 2, 4], 6)        # -> [1, 2]
two_sum([3, 3], 6)           # -> [0, 1]
```

**Think first:** for each number, which other number would finish the pair? Can you look that up fast?

**Hint:** dict `value -> index`. For each `n`, check if `target - n` is already in it.
