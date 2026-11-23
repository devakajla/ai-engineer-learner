# Add two lists item by item

Write `pairwise_sum(a, b)` that returns a list where item `i` is `a[i] + b[i]`. If the lists have different lengths, stop at the shorter one.

```python
pairwise_sum([1, 2, 3], [10, 20, 30])   # -> [11, 22, 33]
pairwise_sum([1, 2, 3], [5])            # -> [6]
```

**Think first:** how do you walk two lists at the same time?

**Hint:** `zip`.
