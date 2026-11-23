# Give a chunk its context

A chunk like `"The limit is 100."` does not say which limit. **Contextual chunks** fix this by adding where the chunk comes from, before you embed it.

Write `contextualize(text, title="", heading="")`.

Rules:
- Build a label from `title` and `heading`, leaving out the ones that are empty, joined with `" > "`.
- If there is a label, return `label + "\n\n" + text`.
- If both are empty, return `text` unchanged.

```python
contextualize("The limit is 100.", "Rate limits", "Free plan")
# -> 'Rate limits > Free plan\n\nThe limit is 100.'
contextualize("The limit is 100.", heading="Free plan")
# -> 'Free plan\n\nThe limit is 100.'
contextualize("Hello")
# -> 'Hello'
```
