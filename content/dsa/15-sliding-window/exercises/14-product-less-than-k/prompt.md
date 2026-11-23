# Subarrays with product less than k

`nums` has **positive** integers. Write `count_product_less(nums, k)` that returns how many contiguous subarrays have a product **strictly less than `k`**.

```python
count_product_less([10, 5, 2, 6], 100)    # -> 8
count_product_less([1, 2, 3], 0)          # -> 0
```

**Think first:** if the window `[lo..hi]` is valid, how many valid subarrays **end at** `hi`? (Every start from `lo` to `hi` works.)

**Hint:** pattern *variable window, count*: multiply in `nums[hi]`; `while product >= k:` divide out `nums[lo]`; then `count += hi - lo + 1`. Watch `k <= 1`.
