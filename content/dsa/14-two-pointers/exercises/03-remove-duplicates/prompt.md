# Remove duplicates from a sorted list

`nums` is sorted. Write `remove_duplicates(nums)` that changes the list **in place** so the first `k` items are the unique values in the same order, and returns `k`. Items after `k` do not matter. No extra list.

```python
nums = [1, 1, 2, 2, 3]
remove_duplicates(nums)    # -> 3, and nums[:3] == [1, 2, 3]
remove_duplicates([])      # -> 0
```

**Think first:** what does the slow pointer point to, and when do you move it?

**Hint:** pattern *reader/writer*. Write `nums[slow] = nums[fast]` when `nums[fast]` differs from the previous item.
