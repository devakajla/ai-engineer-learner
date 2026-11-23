# Filtered search

Write `search_filtered(collection, embed, query, k=3, source=None, heading=None)`. It is like `search`, but it can limit the search to one `source` and/or one `heading`.

Build the `where` filter for Chroma:
- no filter given: do **not** pass `where` (or pass `None`). An empty `{}` is an error in Chroma.
- only `source`: `{"source": source}`
- only `heading`: `{"heading": heading}`
- both: `{"$and": [{"source": source}, {"heading": heading}]}`

Return the same kind of dictionaries as before: `{"id", "text", "source", "heading", "score"}` with `score = 1 - distance`, best first.

Rules:
- Pass `where=` to `collection.query`.
- Ask for no more than the number of chunks that match the filter. Count them with `collection.get(where=where)["ids"]`, or with `collection.count()` when there is no filter.
- If `k <= 0` or nothing matches, return `[]`.

```python
search_filtered(collection, embed, "task", source="auth.md")
# -> only chunks from auth.md
search_filtered(collection, embed, "task", source="tasks.md", heading="List")
# -> only the chunk in tasks.md under "List"
```

**Think first:** how many results can you ask for when the filter matches 2 chunks and `k` is 10?
