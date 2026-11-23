# Chunk a whole document

Build the real chunker. It cuts a markdown file by headings (exercise 3), then packs the paragraphs of each section into chunks of at most `max_chars` (exercise 2), and remembers where each chunk came from.

`pack_paragraphs(text, max_chars)` and `split_markdown(md)` are in the starter. Write `chunk_document(name, md, max_chars)`.

Rules:
- Go through the sections from `split_markdown(md)`, in order.
- For each section, split `section["text"]` with `pack_paragraphs(text, max_chars)`.
- Every chunk is a dictionary: `{"id": f"{name}#{n}", "text": ..., "source": name, "heading": section["heading"]}`.
- `n` counts chunks of the **whole document**: 0, 1, 2, ... (it does not restart for each section).
- An empty document gives `[]`.

```python
md = "# Tasks\n\nCreate a task.\n\n## Delete\n\nUse DELETE.\n\nIt is permanent."
chunk_document("tasks.md", md, 100)
# -> [{'id': 'tasks.md#0', 'text': 'Create a task.', 'source': 'tasks.md', 'heading': 'Tasks'},
#     {'id': 'tasks.md#1', 'text': 'Use DELETE.\n\nIt is permanent.', 'source': 'tasks.md', 'heading': 'Delete'}]
```

These dictionaries are exactly what the next lesson stores in the vector database.

**Think first:** why does each chunk carry `source` and `heading`?
