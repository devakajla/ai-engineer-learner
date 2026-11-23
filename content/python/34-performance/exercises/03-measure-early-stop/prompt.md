# Measure, and stop early

Write two functions:

- `best_time(func, rounds=3, timer=time.perf_counter)` – call `func()` `rounds` times. For each round read `timer()` before and after the call. Return the **smallest** difference. `timer` is given from outside, so tests can pass a fake one. If `rounds < 1`, raise `ValueError`.
- `first_duplicate(iterable)` – return the first value that appears a second time, or `None` if there is none. It must **stop reading as soon as it finds it**: the iterable can be a generator with a million items, or even endless.

```python
ticks = iter([0, 2, 10, 13, 20, 21])           # a fake timer: before/after for 3 rounds
best_time(lambda: None, rounds=3, timer=lambda: next(ticks))   # -> 1   (the rounds took 2, 3 and 1)

first_duplicate([4, 7, 2, 7, 4])               # -> 7
first_duplicate([1, 2, 3])                     # -> None
```

**Think first:** Why do we return the smallest time and not the average? How many items must be read to know the answer for `[4, 7, 2, 7, 4]`?

**Hint:** Collect the round times in a list and return `min(...)`. For `first_duplicate`, keep a `seen` set, and `return` inside the loop at the first item that is already in it.
