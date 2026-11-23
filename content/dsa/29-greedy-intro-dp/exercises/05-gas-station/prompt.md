# Gas station circuit

`gas[i]` is the fuel at station `i`; `cost[i]` is the fuel needed to drive from `i` to the next station. The stations form a circle and the tank starts empty. Write `can_complete_circuit(gas, cost)` that returns the index of the station where you can start and finish a full circle, or `-1`. If an answer exists, it is unique.

```python
can_complete_circuit([1, 2, 3, 4, 5], [3, 4, 5, 1, 2])    # -> 3
can_complete_circuit([2, 3, 4], [3, 4, 3])                # -> -1
```

**Think first:** if total gas is less than total cost, is it possible at all? If your tank drops below 0 starting at `s`, can any station between `s` and the failure be a good start?

**Hint:** pattern *greedy reset*: if `sum(gas) < sum(cost)` return `-1`; else walk with a `tank`; when it goes negative, set `start = i + 1` and `tank = 0`.
