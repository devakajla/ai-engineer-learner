# Describe the arguments

Write `describe(*args, **kwargs)` that returns a tuple `(count_positional, sorted_keyword_names)`.

```python
describe(1, 2, x=5, a=1)   # -> (2, ["a", "x"])
describe()                 # -> (0, [])
```
