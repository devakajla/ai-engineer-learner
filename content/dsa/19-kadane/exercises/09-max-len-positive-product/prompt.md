# Longest subarray with a positive product

Write `max_len_positive_product(nums)` that returns the length of the longest contiguous part whose **product is greater than 0**. Return `0` if none.

```python
max_len_positive_product([1, -2, -3, 4])         # -> 4
max_len_positive_product([0, 1, -2, -3, -4])     # -> 3
```

**Think first:** you only need the **sign** of the product. What breaks a part, and what flips the sign?

**Hint:** pattern *Kadane on signs*: keep `pos` (length of the longest part ending here with a positive product) and `neg` (negative product). A zero resets both to 0; a negative number swaps their roles.
