# Flatten and filter

Write `flatten_positive(matrix)` that takes a list of lists of numbers and returns one flat list with only the **positive** numbers (greater than 0), keeping the order.

```python
flatten_positive([[1, -2], [3], [-4, 5]])   # -> [1, 3, 5]
flatten_positive([[], [0, -1]])             # -> []
```

Use one list comprehension with two `for` parts.
