# Sort a nearly sorted list

Every number in `nums` is at most `k` positions away from its place in the sorted list. Write `sort_nearly_sorted(nums, k)` that returns the sorted list in O(n log k). Use a heap of size `k + 1`.

```python
sort_nearly_sorted([2, 1, 4, 3, 6, 5], 1)    # -> [1, 2, 3, 4, 5, 6]
sort_nearly_sorted([3, 2, 1], 2)             # -> [1, 2, 3]
```

**Think first:** the smallest number must be among the first `k + 1` numbers. What about the next one?

**Hint:** pattern *sliding heap*: push the first `k + 1` numbers; then for each new number do `heappushpop` (see reference) or push and pop; at the end pop the rest.
