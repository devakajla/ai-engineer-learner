# Sort colors (Dutch national flag)

`nums` only contains `0`, `1` and `2`. Write `sort_colors(nums)` that sorts it **in place** in one pass, without `sort`. It returns `None`.

```python
nums = [2, 0, 2, 1, 1, 0]
sort_colors(nums)          # nums is now [0, 0, 1, 1, 2, 2]
```

**Think first:** with three pointers `low`, `mid`, `high`, what is true about everything left of `low` and right of `high`?

**Hint:** `while mid <= high`. `0`: swap with `low`, move both. `2`: swap with `high`, move only `high`. `1`: move `mid`.
