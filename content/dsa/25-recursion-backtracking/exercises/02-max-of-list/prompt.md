# Maximum of a list (recursion)

Write `max_of_list(nums)` that returns the biggest number **using recursion** (no loop, no `max`). The list is not empty.

```python
max_of_list([3, 9, 2])    # -> 9
max_of_list([5])          # -> 5
```

**Think first:** with one item, what is the maximum? With more, how do you combine the first item with the answer for the rest?

**Hint:** pattern *base case + combine*: `if len(nums) == 1: return nums[0]`; else compare `nums[0]` with `max_of_list(nums[1:])`.
