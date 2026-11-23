# Isomorphic strings

Two strings are **isomorphic** if you can replace letters in `s` to get `t`, where each letter always maps to the same letter and **no two letters map to the same one**. Write `is_isomorphic(s, t)`. The strings have the same length.

```python
is_isomorphic("egg", "add")    # -> True
is_isomorphic("foo", "bar")    # -> False
```

**Think first:** is "a maps to x" enough? What about "b also maps to x"?

**Hint:** pattern *two dicts*: one for `s -> t`, one for `t -> s`. If either one disagrees, return `False`.
