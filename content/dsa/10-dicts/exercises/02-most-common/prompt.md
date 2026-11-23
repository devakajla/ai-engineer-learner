# Most common item

Write `most_common(items)` that returns the value that appears most often. If there is a tie, return the one that appears first in the list. The list is not empty.

```python
most_common([1, 2, 2, 3, 3, 3])   # -> 3
most_common(["a", "b", "b", "a"]) # -> "a"
```

**Think first:** count first. Then which item do you pick, and how do you break a tie?

**Hint:** build a counts dict, then loop over the **original list** to find the best.
