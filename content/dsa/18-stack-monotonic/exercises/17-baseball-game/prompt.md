# Baseball game

`ops` is a list of strings that records a game. Write `calc_points(ops)` that returns the **sum of all scores** at the end.

- an integer string (can be negative): you score that number
- `"+"`: you score the sum of the previous two scores
- `"D"`: you score double the previous score
- `"C"`: the previous score is **cancelled** (removed)

The input is always valid.

```python
calc_points(["5", "2", "C", "D", "+"])                       # -> 30
calc_points(["5", "-2", "4", "C", "D", "9", "+", "+"])       # -> 27
```

**Think first:** every rule talks about "the previous score(s)". Which structure gives you the latest items?

**Hint:** pattern *stack of scores*: push for numbers, `+` and `D`; pop for `C`. The answer is `sum(stack)`.
