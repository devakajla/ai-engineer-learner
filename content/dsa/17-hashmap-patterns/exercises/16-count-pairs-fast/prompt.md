# Count pairs with a sum (fast)

Write `count_pairs_sum(nums, target)` that counts the pairs `i < j` with `nums[i] + nums[j] == target`. This is exercise 03 of lesson 13, but now it must be O(n), not O(n²).

```python
count_pairs_sum([1, 5, 7, -1, 5], 6)    # -> 3
count_pairs_sum([1, 1, 1, 1], 2)        # -> 6
```

**Think first:** standing at `x`, how many earlier items would complete the pair?

**Hint:** pattern *seen counter-dict*: `count += seen.get(target - x, 0)`, then add `x` to `seen`.
