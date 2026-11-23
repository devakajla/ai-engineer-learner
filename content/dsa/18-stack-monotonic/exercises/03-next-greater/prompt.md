# Next greater element

Write `next_greater(nums)` that returns a list: for each item, the **first strictly bigger value to its right**, or `-1` if none.

```python
next_greater([4, 1, 2])          # -> [-1, 2, -1]
next_greater([1, 3, 2, 4])       # -> [3, 4, 4, -1]
```

**Think first:** an item that is still waiting for its answer: which items can wait together, and in what order do they get answered?

**Hint:** pattern *monotonic stack (decreasing)*: keep a stack of **indexes** whose answer is not found. For a new `x`, `while stack and nums[stack[-1]] < x:` pop and set that answer to `x`.
