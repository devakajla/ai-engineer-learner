# List the placeholders

Write `placeholders(template)`. It returns the names of the placeholders in a template, **without repeats**, in the order they first appear.

Hint: `string.Formatter().parse(template)` gives tuples `(text, name, spec, conversion)`. `name` is `None` when there is no placeholder in that piece.

```python
placeholders("Hi {name}, you are {age}.")   # -> ['name', 'age']
placeholders("{a} and {b} and {a}")         # -> ['a', 'b']
placeholders("No holes here")               # -> []
```
