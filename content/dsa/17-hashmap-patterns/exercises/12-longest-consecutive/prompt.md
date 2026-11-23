# Longest consecutive run

Write `longest_consecutive(nums)` that returns the length of the longest group of numbers that are consecutive integers (like `1, 2, 3, 4`), in **any order** in the list. It must be O(n): no sorting.

```python
longest_consecutive([100, 4, 200, 1, 3, 2])             # -> 4   (1, 2, 3, 4)
longest_consecutive([0, 3, 7, 2, 5, 8, 4, 6, 0, 1])     # -> 9
```

**Think first:** where does a run start? How can you tell a number is the **start** (its predecessor is missing)?

**Hint:** pattern *set lookup*: put all numbers in a `set`. Only for numbers where `x - 1` is **not** in the set, count upwards `x + 1, x + 2, ...`.
