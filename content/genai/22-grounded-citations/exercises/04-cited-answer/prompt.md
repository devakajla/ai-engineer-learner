# The cited answer, with a repair

Put it all together. In the starter: `format_context`, `build_rag_messages` (lesson 21), `extract_citations`, `check_citations`, `sources_from_answer` (exercises 1 to 3), and `build_cite_messages`, which asks the model to cite.

Write `cited_answer(client, retrieve, question, k=3)`.

Rules:
1. `hits = retrieve(question, k)`. No hits: return `{"answer": "I don't know.", "sources": [], "ok": True}` and make no call.
2. `messages = build_cite_messages(question, hits)`.
3. Make **at most 2** calls: `client.chat.completions.create(model="qwen/qwen3.8-27b", messages=messages, temperature=0, max_completion_tokens=300)`.
4. After each reply `text`:
   - If `text.strip().lower()` starts with `"i don't know"`: return `{"answer": text, "sources": [], "ok": True}`.
   - If `check_citations(text, len(hits))["ok"]`: return `{"answer": text, "sources": sources_from_answer(text, hits), "ok": True}`.
   - Otherwise, for the second try, make a **new** list: the messages, plus an `assistant` message with `text`, plus a `user` message: `f"Your answer must cite sources like [1]. Use only the numbers 1 to {len(hits)}. Rewrite it."`
5. If both replies are bad, return `{"answer": <last text>, "sources": [], "ok": False}`.

```python
cited_answer(client, retrieve, "How do I delete?")
# reply 1: 'Use DELETE.'            (no citation: bad)
# reply 2: 'Use DELETE [1].'
# -> {'answer': 'Use DELETE [1].', 'sources': [{'n': 1, 'source': 'tasks.md', 'heading': 'Delete'}], 'ok': True}
```

**Think first:** why do we allow "I don't know" without a citation?
