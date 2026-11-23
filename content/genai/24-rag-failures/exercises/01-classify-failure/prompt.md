# Where did it fail?

When a RAG answer is wrong, the first question is: **retrieval or generation?** Did the search not find the right chunk, or did it find it and the model still answered badly? The fix is different for each.

Write `classify_failure(expected_ids, retrieved_ids, answer_ok)`.

- `expected_ids`: the ids of chunks that contain the answer (any one of them is enough). An **empty** list means the docs do **not** have the answer.
- `retrieved_ids`: the ids that the search returned.
- `answer_ok`: `True` if the final answer was judged good.

Return one of these texts:
- Empty `expected_ids`: `"ok"` if `answer_ok` else `"hallucination"` (the bot should have said "I don't know").
- No expected id is in `retrieved_ids`: `"retrieval_miss"`.
- Found, but `answer_ok` is false: `"generation_miss"`.
- Found and `answer_ok`: `"ok"`.

```python
classify_failure(["c3"], ["c1", "c2"], False)   # -> 'retrieval_miss'
classify_failure(["c3"], ["c3", "c9"], False)   # -> 'generation_miss'
classify_failure([], ["c1"], False)             # -> 'hallucination'
```

**Think first:** when the answer is wrong **and** the chunk was not found, which one do you fix first?
