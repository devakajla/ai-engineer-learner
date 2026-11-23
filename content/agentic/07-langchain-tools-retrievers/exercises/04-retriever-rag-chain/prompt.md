# A retriever and a RAG chain

A **retriever** is a Runnable that takes a question (a string) and returns a list of `Document`s. A `Document` has `.page_content` (the text) and `.metadata` (a dict, for example the source). In LangChain a RAG chain is just a retriever, a prompt and a model joined with `|`. The imports are given. Write three things:

1. `make_retriever(docs, k=2)`: return `RunnableLambda(search)`, where `search(query)` scores each document by the **number of query words** (lowercase, split on spaces, as a set) that also appear in the document's words, keeps only scores above 0, sorts by score (highest first, ties keep the original order) and returns the top `k` documents.
2. `format_docs(docs)`: numbered passages joined by new lines: `"[1] first text\n[2] second text"`. An empty list gives `""`.
3. `build_rag_chain(retriever, model)`: a prompt with a **system** message `"Answer using only the context. If it is not there, say you do not know."` and a **human** message `"Context:\n{context}\n\nQuestion: {question}"`. The chain is:
   `{"context": retriever | RunnableLambda(format_docs), "question": RunnablePassthrough()} | prompt | model | StrOutputParser()`

`RunnablePassthrough()` hands the original question on, unchanged. You call the chain with just the question string.

```python
chain.invoke("where does tea grow")
# -> 'Assam.'
```

**Think first:** the dict at the start runs two branches on the same question. Which two?

**Hint:** Python's `sort` is stable, so equal scores keep their order. Sort with `key=lambda pair: -pair[0]`.
