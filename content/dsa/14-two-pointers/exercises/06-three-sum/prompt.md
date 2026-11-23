# 3Sum

Write `three_sum(nums)` that returns all **unique** triplets `[a, b, c]` with `a + b + c == 0`. Each triplet is sorted ascending, and the list of triplets is sorted too. `nums` may have repeats; the same triplet must not appear twice.

```python
three_sum([-1, 0, 1, 2, -1, -4])    # -> [[-1, -1, 2], [-1, 0, 1]]
three_sum([0, 0, 0, 0])             # -> [[0, 0, 0]]
```

**Think first:** after you find a triplet, how do you skip equal values so it is not repeated?

**Hint:** sort, fix `i`, run the two-end loop on `i + 1 .. n-1`. Skip `i` if `nums[i] == nums[i-1]`. After a hit, move `left`/`right` past equal values.
