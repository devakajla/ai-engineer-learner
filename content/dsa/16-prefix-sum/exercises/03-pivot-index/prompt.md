# Pivot index

Write `pivot_index(nums)` that returns the **leftmost** index where the sum of the items on the left equals the sum of the items on the right (the item itself is not counted on either side). Return `-1` if there is none.

```python
pivot_index([1, 7, 3, 6, 5, 6])    # -> 3
pivot_index([1, 2, 3])             # -> -1
```

**Think first:** if you know the total and the sum on the left, how do you get the sum on the right without a loop?

**Hint:** pattern *prefix sum with total*: `right = total - left - nums[i]`.
