# Flatten a list of lists

Write `flatten(nested)` that returns one list with all the items of the inner lists, in order. Only one level of nesting.

```python
flatten([[1, 2], [3], [4, 5]])   # -> [1, 2, 3, 4, 5]
flatten([[], [1], []])           # -> [1]
```

**Think first:** two loops: one over inner lists, one over their items.

**Hint:** nested loop with `append`.
