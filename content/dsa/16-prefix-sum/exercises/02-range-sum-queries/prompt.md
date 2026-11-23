# Range sum queries

Write `range_sums(nums, queries)`. Each query is `[left, right]` (both **included**). Return the sum of `nums[left..right]` for every query. There can be many queries, so each one must be O(1) after one O(n) preparation.

```python
range_sums([2, 4, 1, 6, 3], [[0, 2], [1, 3], [4, 4]])    # -> [7, 11, 3]
range_sums([5], [[0, 0]])                                # -> [5]
```

**Think first:** if you know the sum of the first `right + 1` items and the sum of the first `left` items, what is left over?

**Hint:** pattern *prefix sum*: `prefix[0] = 0`, `prefix[i + 1] = prefix[i] + nums[i]`, answer `prefix[right + 1] - prefix[left]`.
