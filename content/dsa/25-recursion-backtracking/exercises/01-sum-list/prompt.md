# Sum of a list (recursion)

Write `sum_list(nums)` that returns the sum of the list **using recursion** (no loop, no `sum`).

```python
sum_list([1, 2, 3, 4])    # -> 10
sum_list([])              # -> 0
```

**Think first:** what is the smallest list you can answer without any work? If you know the sum of everything except the first item, how do you get the full sum?

**Hint:** pattern *base case + smaller problem*: if the list is empty return `0`; else `nums[0] + sum_list(nums[1:])`.
