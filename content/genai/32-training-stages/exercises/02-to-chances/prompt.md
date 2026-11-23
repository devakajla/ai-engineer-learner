# From counts to chances

Counts are not chances yet. Chances in each row must add up to 1.

Write `to_chances(counts)`. `counts` looks like `{word: {next word: count}}`. Return a new dictionary with the same shape, but each number is `count / row total`, rounded to 2 decimal places.

Rules:
- The total of a row is the sum of its counts.
- Use `round(value, 2)`.
- An empty `counts` gives `{}`.
- Do not change the dictionary that was passed in.

**Think first:** What must you work out once per row before you can divide?

**Hint:** `sum(row.values())`.

```python
to_chances({"the": {"cat": 2}, "cat": {"sat": 1, "ran": 3}})
# -> {'the': {'cat': 1.0}, 'cat': {'sat': 0.25, 'ran': 0.75}}

to_chances({})
# -> {}
```
