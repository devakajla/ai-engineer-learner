# Squares of evens (comprehension)

Write `squares_of_evens(nums)` that returns a list with the square of every even number, in order. Use a list comprehension.

```python
squares_of_evens([1, 2, 3, 4])   # -> [4, 16]
squares_of_evens([1, 3])         # -> []
```

**Think first:** read it as: "n * n for each n in nums, only if n is even".

**Hint:** `[expr for x in items if cond]`.
