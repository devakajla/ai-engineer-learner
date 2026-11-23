# First repeated value

Write `first_repeat(items)` that returns the first value that appears a second time while reading from left to right. Return `None` if there are no repeats.

```python
first_repeat([3, 1, 4, 1, 5, 3])   # -> 1
first_repeat([1, 2, 3])            # -> None
```

Use a loop and `break` or an early `return`. Keep a list of the values you have already seen.
