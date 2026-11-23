# Format the context

The model reads the retrieved chunks as text in the prompt. Number them, so the answer can point to them later (lesson 22).

Write `format_context(hits)`. Each hit has `text`, `source` and `heading` (the heading can be empty or missing).

Rules:
- Each hit becomes a block: `"[n] label\ntext"`, where `n` counts from 1.
- The label is the `source`. If the hit has a non-empty `heading`, the label is `source + " > " + heading`.
- Blocks are joined with a blank line (`"\n\n"`).
- No hits gives the empty string `""`.

```python
hits = [
    {"text": "Use DELETE.", "source": "tasks.md", "heading": "Delete"},
    {"text": "Send a token.", "source": "auth.md", "heading": ""},
]
print(format_context(hits))
# [1] tasks.md > Delete
# Use DELETE.
#
# [2] auth.md
# Send a token.
```
