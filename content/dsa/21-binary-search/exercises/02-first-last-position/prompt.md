# First and last position

`nums` is sorted ascending and may have **duplicates**. Write `search_range(nums, target)` that returns `[first_index, last_index]` of `target`, or `[-1, -1]` if it is missing. O(log n).

```python
search_range([5, 7, 7, 8, 8, 10], 8)    # -> [3, 4]
search_range([5, 7, 7, 8, 8, 10], 6)    # -> [-1, -1]
```

**Think first:** when you find `target` at `mid`, is it the first one? What should you do to look for an earlier one?

**Hint:** pattern *lower bound / upper bound*: run the search twice. For the first index, when `nums[mid] == target` save `mid` and keep searching **left** (`hi = mid - 1`); for the last, keep searching **right**.
