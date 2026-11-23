# Merge two sorted lists (the lazy way)

Write `merge_sorted(a, b)`: both lists are already sorted. Return one new sorted list with all items. Here use the lazy way: join the lists and sort. It costs O(n log n). In the next lesson you will do it in O(n) with two pointers.

```python
merge_sorted([1, 3, 5], [2, 4, 6])    # -> [1, 2, 3, 4, 5, 6]
merge_sorted([], [1])                 # -> [1]
```

**Think first:** the input is already sorted. What work is "wasted" when you call `sort` on the joined list?

**Hint:** `sorted(a + b)`. Do not change `a` or `b`.
