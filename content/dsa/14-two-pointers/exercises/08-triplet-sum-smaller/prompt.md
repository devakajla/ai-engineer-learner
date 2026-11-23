# Triplets with sum smaller than target

Write `triplets_smaller(nums, target)` that counts triplets of positions `i < j < k` with `nums[i] + nums[j] + nums[k] < target`. Aim for O(n²).

```python
triplets_smaller([-2, 0, 1, 3], 2)    # -> 2     ((-2,0,1) and (-2,0,3))
triplets_smaller([1, 2], 5)           # -> 0
```

**Think first:** if `nums[i] + nums[left] + nums[right] < target` in a sorted list, how many other choices for `right` also work?

**Hint:** sort, fix `i`. If the sum is smaller than target, **every** index from `left+1` to `right` pairs with `left`: add `right - left` and move `left` up. Otherwise move `right` down.
