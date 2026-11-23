# All permutations

`nums` has **different** numbers. Write `permutations(nums)` that returns all orderings as lists. Any order of the results. (Do not import `itertools`.)

```python
permutations([1, 2, 3])    # -> 6 lists, e.g. [1, 2, 3], [1, 3, 2], ...
permutations([])           # -> [[]]
```

**Think first:** for the first position, how many numbers can you choose? After choosing, what is left?

**Hint:** pattern *choose one unused*: keep a `used` list of booleans; at each step try every unused number, mark it, recurse, then unmark (backtrack).
