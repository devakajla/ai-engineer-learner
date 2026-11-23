# Validate age

Write `parse_age(text)` that returns the age as an `int`.

- If `text` is not a whole number, raise `ValueError("age must be a number")`.
- If the number is below 0 or above 150, raise `ValueError("age out of range")`.

```python
parse_age("25")     # -> 25
parse_age("abc")    # raises ValueError("age must be a number")
parse_age("-1")     # raises ValueError("age out of range")
```
