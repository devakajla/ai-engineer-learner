# Add chunks to a collection

Write `add_chunks(collection, embed, chunks)`. Each chunk is a dictionary `{"id", "source", "heading", "text"}`.

Rules:
- Embed all the texts with **one** call: `embed(texts)`. It returns one vector per text.
- Call `collection.upsert(...)` with `ids`, `documents`, `embeddings` and `metadatas`. The metadata of a chunk is `{"source": ..., "heading": ...}`.
- Keep the order of the chunks in every list.
- Return how many chunks were added.
- If `chunks` is empty: return `0`, and call neither `embed` nor `upsert`.

```python
chunks = [
    {"id": "t.md:0", "source": "t.md", "heading": "Delete", "text": "Use DELETE."},
    {"id": "t.md:1", "source": "t.md", "heading": "", "text": "Use GET."},
]
add_chunks(collection, embed, chunks)   # -> 2
collection.count()                      # -> 2
add_chunks(collection, embed, [])       # -> 0
```

**Think first:** which four lists does `upsert` need, and what must be true about them?

**Hint:** list comprehensions: `[c["id"] for c in chunks]`.
