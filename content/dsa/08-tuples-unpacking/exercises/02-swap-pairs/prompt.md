# Swap neighbours

Write `swap_pairs(nums)` that returns a new list where each pair of neighbours is swapped: items 0 and 1, items 2 and 3, and so on. If the length is odd, the last item stays.

```python
swap_pairs([1, 2, 3, 4])      # -> [2, 1, 4, 3]
swap_pairs([1, 2, 3])         # -> [2, 1, 3]
```

**Think first:** which indexes do you visit? Step by 2.

**Hint:** copy the list, loop `range(0, len(nums) - 1, 2)`, swap with `a[i], a[i+1] = a[i+1], a[i]`.
