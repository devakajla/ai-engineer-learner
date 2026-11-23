# Last stone weight

Each turn, take the two heaviest stones. If they weigh the same, both are destroyed; otherwise the heavier one is left with weight `heavy - light`. Repeat until at most one stone is left. Write `last_stone_weight(stones)` that returns the weight of the last stone (`0` if none).

```python
last_stone_weight([2, 7, 4, 1, 8, 1])    # -> 1
last_stone_weight([5])                   # -> 5
```

**Think first:** you need the **biggest** two each time. Python's heap gives the smallest. What can you push instead?

**Hint:** pattern *max-heap with negatives*: push `-w`; pop two; if different, push the difference back.
