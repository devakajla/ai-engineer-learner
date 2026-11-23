# Minimum cost to connect ropes

`ropes` are lengths. Joining two ropes of lengths `a` and `b` costs `a + b` and makes one rope. Write `min_cost_ropes(ropes)` that returns the **minimum total cost** to join all ropes into one (`0` if there is 0 or 1 rope).

```python
min_cost_ropes([4, 3, 2, 6])    # -> 29
min_cost_ropes([1, 2, 3])       # -> 9
```

**Think first:** the cost of a rope is paid again every time it is joined later. Which ropes should be joined first?

**Hint:** pattern *greedy with a min-heap*: pop the two smallest, add their sum to the cost, push the sum back.
