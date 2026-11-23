# Container with most water

`heights[i]` is the height of a vertical line at position `i`. Pick two lines. They form a container whose area is `min(h1, h2) * distance`. Write `max_water(heights)` that returns the biggest area. Aim for O(n).

```python
max_water([1, 8, 6, 2, 5, 4, 8, 3, 7])    # -> 49
max_water([1, 1])                         # -> 1
```

**Think first:** the width shrinks every step. What must grow for the area to grow? Which line limits the height?

**Hint:** opposite ends. Compute the area, then move the pointer at the **shorter** line (moving the taller one cannot help).
