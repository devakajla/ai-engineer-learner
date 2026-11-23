# Pack paragraphs

Write `pack_paragraphs(text, max_chars)`. Paragraphs are separated by a blank line (`"\n\n"`). Join neighbouring paragraphs into chunks, with `"\n\n"` between them, as long as the chunk stays at most `max_chars` characters.

Rules:
- Strip each paragraph and ignore empty ones.
- Keep the paragraph order. Start a new chunk when the next paragraph does not fit.
- A single paragraph longer than `max_chars` stays alone in its own chunk (do not cut it).
- Raise `ValueError` if `max_chars <= 0`.
- No paragraphs gives `[]`.

```python
text = "aa\n\nbb\n\ncc\n\ndd"
pack_paragraphs(text, 8)    # -> ['aa\n\nbb', 'cc\n\ndd']
pack_paragraphs(text, 100)  # -> ['aa\n\nbb\n\ncc\n\ndd']
pack_paragraphs("a long paragraph here\n\nhi", 5)   # -> ['a long paragraph here', 'hi']
pack_paragraphs("  \n\n  ", 5)                      # -> []
```

**Think first:** what must you do after the loop ends?
