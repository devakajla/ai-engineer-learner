# Ways to split an array

Write `num_ways_split(nums)` that counts the indexes `i` (from `0` to `len(nums) - 2`) where the sum of `nums[0..i]` is **greater than or equal to** the sum of `nums[i + 1..]`. Both sides must have at least one item.

```python
num_ways_split([10, 4, -8, 7])    # -> 2
num_ways_split([2, 3, 1, 0])      # -> 2
```

**Think first:** how do you get the right sum from the total and the left sum?

**Hint:** pattern *prefix sum with total*.
