# Rerank the hits

Vector search is fast but rough. A **reranker** looks at the question and each candidate **together** and gives a better score. It is slower, so you use it only on a short list (for example the top 20), and keep the best few.

`by_rerank(hit)` (gives the `"rerank_score"` of a hit, for sorting) is in the starter. Write `rerank(score_fn, question, hits, top_n)`.

`score_fn(question, text)` is a function you are given. It returns a number: higher means a better match. (A real one is a reranker model. In tests it is a tiny fake.)

Rules:
- For every hit make a **copy** and add `"rerank_score": score_fn(question, hit["text"])`.
- Sort by `rerank_score`, best first. Equal scores keep their old order.
- Return the first `top_n` hits. If `top_n <= 0`, return `[]`.
- Do not change the original hit dictionaries.

```python
def overlap(question, text):               # a toy scorer: shared words
    return len(set(question.split()) & set(text.split()))

hits = [{"id": "a", "text": "weather today"}, {"id": "b", "text": "delete a task"}]
rerank(overlap, "delete task", hits, 1)
# -> [{'id': 'b', 'text': 'delete a task', 'rerank_score': 2}]
```

**Think first:** why not rerank all 10,000 chunks?
