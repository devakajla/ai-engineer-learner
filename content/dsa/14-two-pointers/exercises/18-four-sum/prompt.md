# 4Sum

Write `four_sum(nums, target)` that returns all **unique** quadruplets `[a, b, c, d]` (each sorted ascending) with sum `target`. The list of quadruplets is sorted too. Aim for O(n³).

```python
four_sum([1, 0, -1, 0, -2, 2], 0)    # -> [[-2, -1, 1, 2], [-2, 0, 0, 2], [-1, 0, 0, 1]]
four_sum([2, 2, 2, 2, 2], 8)         # -> [[2, 2, 2, 2]]
```

**Think first:** 3Sum fixed one number. How many do you fix for 4Sum, and what stays for the two pointers?

**Hint:** sort; two nested loops fix `i` and `j` (skip equal values); two-end loop on the rest; skip duplicates after a hit.
