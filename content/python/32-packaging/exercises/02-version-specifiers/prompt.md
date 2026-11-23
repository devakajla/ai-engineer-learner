# Does this version fit the rule?

Write two functions:

- `parse_version(text)` → a tuple of ints. `"1.10.0"` becomes `(1, 10, 0)`. Raise `ValueError` if a part is not a whole number (for example `"1.x.0"` or `""`).
- `satisfies(version, rule)` → `True` if `version` (text) fits `rule` (text). A rule is one or more conditions joined by commas, like `">=1.4,<2.0"`. Supported operators: `==`, `!=`, `>=`, `<=`, `>`, `<`. An empty rule (`""`) accepts every version. Spaces around parts are ignored. An unknown operator raises `ValueError`.

Compare versions as **numbers**, and treat a shorter version as if it ended with zeros: `"1.4"` equals `"1.4.0"`.

```python
parse_version("1.10.0")                 # -> (1, 10, 0)
satisfies("1.10.0", ">=1.9,<2.0")       # -> True
satisfies("2.0.0", ">=1.9,<2.0")        # -> False
```

**Think first:** Why is `"1.10" > "1.9"` the wrong way to compare? How can `(1, 4)` and `(1, 4, 0)` be made equal?

**Hint:** Pad both tuples with zeros to the same length. Check the **two-character** operators (`>=`, `<=`, `==`, `!=`) before the one-character ones. Use `all(...)` over the conditions.
