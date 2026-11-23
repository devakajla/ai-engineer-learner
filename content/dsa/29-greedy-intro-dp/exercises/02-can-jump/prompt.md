# Can you reach the end?

`nums[i]` is the farthest you can jump forward from index `i`. You start at index 0. Write `can_jump(nums)` that returns `True` if you can reach the last index.

```python
can_jump([2, 3, 1, 1, 4])    # -> True
can_jump([3, 2, 1, 0, 4])    # -> False
```

**Think first:** you do not need the path, only the farthest index you can reach so far.

**Hint:** pattern *greedy: farthest reach*: `reach = 0`; for each `i`: if `i > reach` return `False`; `reach = max(reach, i + nums[i])`.
