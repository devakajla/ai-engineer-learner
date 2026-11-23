# Move zeros to the end

Write `move_zeros(nums)` that returns a new list with all zeros moved to the end. Other numbers keep their order.

```python
move_zeros([0, 1, 0, 3, 12])   # -> [1, 3, 12, 0, 0]
move_zeros([0, 0])             # -> [0, 0]
```

**Think first:** how many zeros are there? Where do the non-zeros go?

**Hint:** build a list of non-zeros, then add the zeros.
