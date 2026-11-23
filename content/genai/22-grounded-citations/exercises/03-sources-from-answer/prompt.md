# Show the sources

The user should see **where** an answer came from. Turn the citation numbers into sources.

`extract_citations(answer)` is in the starter. Write `sources_from_answer(answer, hits)`. `hits` is the list that was put in the prompt, in order, so `[1]` is `hits[0]`.

Rules:
- For each cited number (in the order of first appearance) that is valid (1 to `len(hits)`), add `{"n": n, "source": hit["source"], "heading": hit.get("heading", "")}`.
- Ignore numbers that are out of range.

```python
hits = [{"source": "tasks.md", "heading": "Delete", "text": "..."},
        {"source": "auth.md", "text": "..."}]
sources_from_answer("Use DELETE [1]. Send a token [2].", hits)
# -> [{'n': 1, 'source': 'tasks.md', 'heading': 'Delete'},
#     {'n': 2, 'source': 'auth.md', 'heading': ''}]
sources_from_answer("Made up [9].", hits)   # -> []
```
