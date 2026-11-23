# Batch any iterable

Bulk-inserting into a database or sending embeddings to an API is done in **batches**. Write a generator `chunked(iterable, size)` that yields lists of up to `size` items.

- Works for **any iterable**, including generators and infinite ones (so you can't use `len()` or slicing on the input).
- The last batch may be smaller. No empty batch at the end.
- `size < 1` → `ValueError` (raise it **when called**, before iterating — hint: validate in a normal function that returns the generator).

```python
list(chunked([1, 2, 3, 4, 5], 2))   # -> [[1, 2], [3, 4], [5]]
list(chunked([], 3))                # -> []
g = chunked(itertools.count(), 3); next(g)   # -> [0, 1, 2]
```
