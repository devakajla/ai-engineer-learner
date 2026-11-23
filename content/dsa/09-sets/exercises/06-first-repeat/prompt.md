# First repeated value

Write `first_repeat(items)` that returns the first value that appears a second time while scanning left to right. If nothing repeats, return `None`.

```python
first_repeat([3, 1, 4, 1, 3])   # -> 1
first_repeat([1, 2, 3])         # -> None
```

**Think first:** "first repeat" is decided by the **second** occurrence, not the first. Check the example: 3 repeats at the end, but 1 repeats earlier.

**Hint:** seen-set; return when you meet a value already seen.
