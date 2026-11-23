# A tiny agentic step: pick the source

In **agentic RAG** the model makes decisions: which source to search, whether to search again. The smallest decision is **routing**: pick the right knowledge source for a question.

Write `choose_source(client, question, sources)`. `sources` is `{name: description}`, for example `{"api": "REST API docs", "hr": "HR policies"}`.

Rules:
1. Build a system message that lists the sources, one per line as `name: description`, and tells the model to reply with only a source name, or `none`.
2. Call `client.chat.completions.create(model="qwen/qwen3.8-27b", messages=[system, user], temperature=0)`. The user message is the question.
3. Clean the reply: `strip()`, `lower()`, and remove a final dot (`strip(".")`).
4. If the cleaned reply is one of the source names, return it. Otherwise (including `"none"` or any made-up name) return `None`.

(Source names are lower case in the tests.)

```python
choose_source(client, "How do I take leave?", {"api": "REST API docs", "hr": "HR policies"})
# the client replies "HR."   ->   'hr'
```

**Think first:** why not trust the reply without checking it against `sources`?
