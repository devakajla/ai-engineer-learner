# Render a stored prompt

Combine your two earlier functions. `render(template, values)` and `get_prompt(registry, name, version=None)` are **given** in `starter.py`. Do not change them.

Write `render_prompt(registry, name, values, version=None)`:
- Get the template with `get_prompt`.
- Fill it with `render`.
- Return the finished prompt.

Rules:
- An unknown name or version raises `KeyError` (from `get_prompt`).
- A missing value raises `ValueError("missing variable: <name>")` (from `render`).
- With `version=None`, use the latest version.

**Think first:** Which function runs first, and what does the second one receive?

**Hint:** Two lines.

```python
registry = {"qa": {"v1": "Answer: {question}", "v2": "Answer briefly: {question}"}}

render_prompt(registry, "qa", {"question": "What is an API?"})
# -> 'Answer briefly: What is an API?'

render_prompt(registry, "qa", {"question": "Hi"}, version="v1")
# -> 'Answer: Hi'
```
