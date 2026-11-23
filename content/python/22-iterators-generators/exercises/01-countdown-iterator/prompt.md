# An iterator class and a generator

Write the same countdown twice:

1. `class Countdown` implementing the iterator protocol (`__iter__` + `__next__`): `list(Countdown(3)) == [3, 2, 1]`
2. a generator function `countdown(start)` that yields the same values

Both must yield nothing for `start <= 0`, and a `Countdown` instance must be **exhausted after one pass** (like every iterator).

```python
c = Countdown(2)
list(c)   # -> [2, 1]
list(c)   # -> []
list(countdown(3))   # -> [3, 2, 1]
```
