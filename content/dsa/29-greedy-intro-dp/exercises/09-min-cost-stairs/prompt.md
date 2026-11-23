# Min cost climbing stairs

`cost[i]` is the price of stepping **on** stair `i`. After paying, you may climb 1 or 2 stairs. You may start on stair 0 or 1. The top is one step past the last stair. Write `min_cost(cost)` that returns the cheapest way to reach the top.

```python
min_cost([10, 15, 20])                       # -> 15
min_cost([1, 100, 1, 1, 1, 100, 1, 1, 100, 1])    # -> 6
```

**Think first:** the cheapest cost to be able to stand at stair `i` depends on which two earlier stairs?

**Hint:** pattern *1D DP*: `reach[i] = min(reach[i-1] + cost[i-1], reach[i-2] + cost[i-2])` with `reach[0] = reach[1] = 0`; answer is `reach[n]`.
