# A failure report

Run a test set, then count **which kind** of failure happens most. That tells you where to work.

`classify_failure` (exercise 1) is in the starter, with the list `CATEGORIES` in the solution. Write `failure_report(results)`. Each result is a dictionary:
`{"question": ..., "expected": [...], "retrieved": [...], "answer_ok": ...}`.

Return `{"counts": {...}, "by_category": {...}}`:
- `counts[name]`: how many results fall into each category.
- `by_category[name]`: the list of their questions, in order.
- Both dictionaries must have **all four** names, even when a count is 0: `"ok"`, `"retrieval_miss"`, `"generation_miss"`, `"hallucination"`.

The constant `CATEGORIES = ["ok", "retrieval_miss", "generation_miss", "hallucination"]` is in your starter.

```python
results = [
    {"question": "q1", "expected": ["a"], "retrieved": ["a"], "answer_ok": True},
    {"question": "q2", "expected": ["b"], "retrieved": ["x"], "answer_ok": False},
]
failure_report(results)["counts"]
# -> {'ok': 1, 'retrieval_miss': 1, 'generation_miss': 0, 'hallucination': 0}
```
