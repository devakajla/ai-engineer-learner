# Squares of a sorted list

`nums` is sorted ascending and may have negatives. Write `sorted_squares(nums)` that returns a sorted list of the squares in **O(n)** (no `sort`).

```python
sorted_squares([-4, -1, 0, 3, 10])    # -> [0, 1, 9, 16, 100]
sorted_squares([-7, -3, 2, 3, 11])    # -> [4, 9, 9, 49, 121]
```

**Think first:** where is the **biggest** square: in the middle or at one of the two ends?

**Hint:** pattern *opposite ends*. Compare `abs(nums[left])` and `abs(nums[right])`, put the bigger square at the **back** of the result and move that pointer.
