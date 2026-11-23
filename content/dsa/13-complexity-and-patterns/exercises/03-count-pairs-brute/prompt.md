# Count pairs (brute force)

Write `count_pairs(nums, target)` that returns how many pairs of positions `i < j` have `nums[i] + nums[j] == target`. Use the plain double loop: O(n²).

```python
count_pairs([1, 2, 3, 4], 5)    # -> 2    (1+4 and 2+3)
count_pairs([2, 2, 2], 4)       # -> 3    (three different pairs of positions)
```

**Think first:** why must the inner loop start at `i + 1`?

**Hint:** `for j in range(i + 1, len(nums))` so each pair is counted once. Pattern: *counter* + nested loops.
