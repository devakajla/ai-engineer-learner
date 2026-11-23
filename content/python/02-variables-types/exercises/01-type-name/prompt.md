# Name the type

Write `type_name(value)` that returns the **name** of the value's type as a string.

```python
type_name(5)        # -> "int"
type_name("hi")     # -> "str"
type_name(None)     # -> "NoneType"
type_name([1, 2])   # -> "list"
```

Hint: every type object has a `__name__` attribute.
