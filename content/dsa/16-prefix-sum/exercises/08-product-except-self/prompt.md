# Product of the rest

Write `product_except_self(nums)` that returns a list where item `i` is the product of **all items except `nums[i]`**. Do **not** use division. O(n) time.

```python
product_except_self([1, 2, 3, 4])    # -> [24, 12, 8, 6]
product_except_self([2, 0, 3])       # -> [0, 6, 0]
```

**Think first:** the answer for `i` is (product of everything left of `i`) times (product of everything right of `i`).

**Hint:** pattern *prefix and suffix*: one pass left to right filling "product before", one pass right to left multiplying "product after".
