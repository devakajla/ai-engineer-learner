# Render a template

Write `render(template, values)`. It fills the placeholders of `template` with the dictionary `values`.

Rules:
- Use `template.format(**values)`.
- If a placeholder has no value, raise `ValueError` with the message `"missing variable: <name>"`.
- Extra values are allowed and ignored.

```python
render("Hi {name}!", {"name": "Dev"})          # -> 'Hi Dev!'
render("Hi {name}!", {"name": "Dev", "x": 1})  # -> 'Hi Dev!'
render("Hi {name}!", {})                       # raises ValueError: missing variable: name
```
