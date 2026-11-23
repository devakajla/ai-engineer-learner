# Has a pair (fast)

Write `has_pair(nums, target)` that returns `True` if two **different positions** add up to `target`, else `False`. It must be O(n): the tests use a big list, so a double loop will be too slow.

```python
has_pair([2, 7, 11, 15], 9)    # -> True    (2 + 7)
has_pair([3, 3], 6)            # -> True    (two different positions)
has_pair([3], 6)               # -> False
```

**Think first:** for each number `x`, which other number would complete the pair?

**Hint:** keep a set of numbers already seen and check `target - x in seen`. Pattern: *seen-set*.
