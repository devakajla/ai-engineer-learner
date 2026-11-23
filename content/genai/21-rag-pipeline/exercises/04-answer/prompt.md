# The RAG answer

Join retrieval and generation. `format_context`, `RAG_SYSTEM` and `build_rag_messages` (exercises 2 and 3) are in the starter.

Write `answer(client, retrieve, question, k=3, min_score=0.0)`. `retrieve` is a **function**: `retrieve(question, k)` returns a list of hits, each with a `"score"`.

Rules:
1. `hits = retrieve(question, k)`, then keep only hits with `score >= min_score`.
2. If no hits are left, return `{"answer": "I don't know.", "hits": []}` and make **no** model call. The model would only guess.
3. Otherwise build the messages with `build_rag_messages(question, hits)` and call `client.chat.completions.create(model="qwen/qwen3.8-27b", messages=messages, temperature=0, max_completion_tokens=300)`.
4. Return `{"answer": <reply text>, "hits": hits}`.

```python
answer(client, retrieve, "How do I delete a task?", k=2)
# -> {'answer': 'Use the DELETE endpoint [1].', 'hits': [...2 hits...]}
answer(client, retrieve_nothing, "Best pizza?")
# -> {'answer': "I don't know.", 'hits': []}      (and no call to the model)
```

**Think first:** why is a call with no context worse than no call?
