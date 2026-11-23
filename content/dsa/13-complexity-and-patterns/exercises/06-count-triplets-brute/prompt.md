# Count triplets (brute force)

Write `count_triplets(nums, target)` that returns how many triples of positions `i < j < k` have `nums[i] + nums[j] + nums[k] == target`. Use three loops: O(n³). Feel how slow it is; the next lesson fixes it.

```python
count_triplets([1, 2, 3, 4, 5], 9)    # -> 2    (1+3+5 and 2+3+4)
count_triplets([0, 0, 0, 0], 0)       # -> 4
```

**Think first:** how many triples exist for `n = 100`? Would `n = 10**5` finish?

**Hint:** `j` starts at `i + 1`, `k` starts at `j + 1`.
