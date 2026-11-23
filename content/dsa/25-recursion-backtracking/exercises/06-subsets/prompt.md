# All subsets

`nums` has **different** numbers. Write `subsets(nums)` that returns all subsets (including the empty one) as lists. Keep the numbers inside each subset in the same order as in `nums`. The order of the subsets does not matter.

```python
subsets([1, 2])       # -> [[], [1], [2], [1, 2]]   (any order)
subsets([])           # -> [[]]
```

**Think first:** for each number you make a choice: take it or skip it. How many choices in total for `n` numbers?

**Hint:** pattern *take / skip*: `def go(i, current):` if `i == len(nums)`: save a copy of `current`; else skip `nums[i]`, then take it (append), recurse, and **undo** (`pop`).
