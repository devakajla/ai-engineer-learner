# Most frequent value

Write `most_frequent(nums)` that returns the value that appears the most. If several values tie, return the **smallest** of them. Return `None` for an empty list.

```python
most_frequent([1, 3, 2, 3, 2])    # -> 2
most_frequent([5])                # -> 5
```

**Think first:** after counting, how do you pick the winner and break ties without sorting?

**Hint:** pattern *counter-dict + max tracking*: update the best when the count is higher, or equal with a smaller value.
