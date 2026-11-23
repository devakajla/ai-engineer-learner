# Remove repeats

Retrieved chunks often repeat: the same text in two files, or ten chunks from one long page. Repeats waste the context and push out other useful chunks.

Write `dedupe_hits(hits, max_per_source=None)`. Each hit has `"text"` and `"source"` (the source may be missing).

Rules:
- Two hits are the **same** when their texts are equal after making them lower case and squeezing spaces (`" ".join(text.lower().split())`). Keep the **first**, drop the later ones.
- If `max_per_source` is not `None`, keep at most that many hits from each `source`. A missing source counts as `""`.
- Keep the original order. Do not change the hit dictionaries.
- A hit that is dropped as a repeat does **not** count for its source.

```python
hits = [
    {"id": 1, "text": "Use DELETE.", "source": "a.md"},
    {"id": 2, "text": "use   delete.", "source": "b.md"},
    {"id": 3, "text": "Other.", "source": "a.md"},
]
dedupe_hits(hits)                      # -> hits 1 and 3
dedupe_hits(hits, max_per_source=1)    # -> hit 1 only (hit 2 is a repeat, hit 3 is a second one from a.md)
```
