# Make hits

A retriever finds the chunks that are most like the question. In this exercise you do the last step of a retriever: join each chunk with its score, sort, and cut.

`hit_score(hit)` is in the starter (it gives the score of a hit; you can use it as `key=hit_score` in `sorted`). Write `make_hits(chunks, scores, k, min_score=0.0)`.

`chunks` is a list of dictionaries (`id`, `text`, `source`, `heading`). `scores[i]` is the score of `chunks[i]`.

Rules:
- Make a **copy** of each chunk and add the key `"score"`. Do not change the original chunk dictionaries.
- Sort best score first. Equal scores keep their original order.
- Keep the first `k`, then drop every hit whose score is below `min_score`.
- If `k <= 0`, return `[]`.

```python
chunks = [{"id": "a", "text": "x", "source": "s", "heading": ""},
          {"id": "b", "text": "y", "source": "s", "heading": ""}]
make_hits(chunks, [0.2, 0.9], k=1)
# -> [{'id': 'b', 'text': 'y', 'source': 's', 'heading': '', 'score': 0.9}]
make_hits(chunks, [0.2, 0.9], k=5, min_score=0.5)
# -> [{'id': 'b', ..., 'score': 0.9}]       (the 0.2 hit is dropped)
```
