# Grade the documents

Plain RAG (GenAI lesson 21) retrieves chunks and answers, even when the chunks are useless. **Agentic RAG** adds a check: a model **grades** each chunk ("is this relevant?") and the graph decides what to do next. This exercise builds the grader.

The starter gives you `ask(client, prompt, system=None, temperature=0)`: one model call, returns the stripped reply text. Write:

1. `grade_doc(client, question, doc)`: return `True` if the model says the document is relevant. Send exactly this prompt (use an f-string, note the blank lines):
   `f"Question: {question}\n\nDocument: {doc}\n\nIs the document relevant to the question? Answer yes or no."`
   The answer counts as relevant only if the reply, in lower case with spaces at both ends removed, **starts with** `"yes"`. Anything else (`"no"`, `"maybe"`) is `False`.
2. `grade_docs(client, question, docs)`: return the list of docs for which `grade_doc` is true, in the same order. One model call per doc.

```python
grade_docs(client, "refund time?", ["Refund takes 5 days", "Cats sleep a lot"])
# -> ['Refund takes 5 days']
```

**Think first:** why is "only a clear yes counts" the safer rule?

**Hint:** `reply.strip().lower().startswith("yes")`.
