# Largest rectangle in a histogram

`heights[i]` is the height of a bar of width 1. Write `largest_rectangle(heights)` that returns the area of the **largest rectangle** that fits inside the bars.

```python
largest_rectangle([2, 1, 5, 6, 2, 3])    # -> 10   (bars 5 and 6, width 2)
largest_rectangle([2, 4])                # -> 4
```

**Think first:** for one bar as the shortest, how far can the rectangle go left and right? Which bars stop it?

**Hint:** pattern *monotonic stack (increasing)*: when a shorter bar arrives, pop taller bars; for each popped bar the width runs from the new stack top + 1 to `i - 1`. Add a `0` bar at the end to flush the stack.
