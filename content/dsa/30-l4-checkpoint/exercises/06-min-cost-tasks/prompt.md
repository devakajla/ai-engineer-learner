# Connect ropes in groups of two

You have `sticks` with lengths. Joining two sticks costs the sum of their lengths, and the result is a new stick. Write `min_join_cost(sticks)` that returns the smallest total cost to end with one stick (`0` if there are 0 or 1 sticks).

```python
min_join_cost([2, 4, 3])     # -> 14
min_join_cost([7])           # -> 0
```

**Think first:** which two sticks should you join first?

**Hint:** pattern *greedy + heap*: always join the two smallest; push the result back.
