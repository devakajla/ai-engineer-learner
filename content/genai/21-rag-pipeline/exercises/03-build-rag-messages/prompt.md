# Build the RAG messages

Write `build_rag_messages(question, hits)`. It returns the `messages` list for one RAG call. `format_context` (exercise 2) and the constant `RAG_SYSTEM` are in the starter.

Rules:
- The first message is the `system` message with the content `RAG_SYSTEM`.
- The second is the `user` message with this content: `"Context:\n" + context + "\n\nQuestion: " + question`.
- `context` is `format_context(hits)`. If there are no hits, use the text `"(no context)"` instead.

```python
build_rag_messages("How do I delete?", [{"text": "Use DELETE.", "source": "tasks.md", "heading": ""}])
# -> [{'role': 'system', 'content': "Answer the question using only the context. If the answer is not in the context, reply exactly: I don't know."},
#     {'role': 'user', 'content': 'Context:\n[1] tasks.md\nUse DELETE.\n\nQuestion: How do I delete?'}]
```
