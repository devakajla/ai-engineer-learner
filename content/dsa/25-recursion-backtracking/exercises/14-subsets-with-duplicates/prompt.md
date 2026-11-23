# Subsets with duplicate numbers

`nums` may contain **repeated** numbers. Write `subsets_with_dup(nums)` that returns all **different** subsets (as sorted lists). No two returned subsets may be equal. Any order.

```python
subsets_with_dup([1, 2, 2])    # -> [[], [1], [1, 2], [1, 2, 2], [2], [2, 2]]   (any order)
subsets_with_dup([0])          # -> [[], [0]]
```

**Think first:** if you sort `nums`, equal numbers are neighbours. When would taking the second `2` before the first `2` create a duplicate subset?

**Hint:** pattern *skip equal siblings*: sort; `go(start)`: save the current subset; for `i` in `start..`: `if i > start and nums[i] == nums[i - 1]: continue`; append, `go(i + 1)`, pop.
