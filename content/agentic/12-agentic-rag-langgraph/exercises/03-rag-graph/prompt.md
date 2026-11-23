# The agentic RAG graph

Now wire it together as a LangGraph graph with a **loop**: retrieve, grade, then answer, or rewrite and retrieve again, or give up.

```
START -> retrieve -> grade --(relevant)--> answer -> END
                       |--(none, tries left)--> rewrite -> retrieve (loop)
                       |--(none, no tries)----> give_up -> END
```

The starter gives you the imports, `ask`, `grade_docs`, `decide_next`, `rewrite_question` and the `RagState` shape (`question`, `docs`, `relevant`, `tries`, `max_tries`, `answer`). Write `build_rag_graph(client, search)`. `search(question)` is a function that returns a list of text chunks. Inside it, define the node functions (they can use `client` and `search` from the outer function) and build the graph:

- `retrieve(state)`: `{"docs": search(state["question"]), "tries": state["tries"] + 1}`
- `grade(state)`: `{"relevant": grade_docs(client, state["question"], state["docs"])}`
- `rewrite(state)`: `{"question": rewrite_question(client, state["question"])}`
- `answer(state)`: build `"Answer using only this context.\n\nContext:\n" + "\n".join(state["relevant"]) + "\n\nQuestion: " + state["question"]` and return `{"answer": ask(client, prompt)}`
- `give_up(state)`: `{"answer": "I could not find this in the documents."}` (no model call)

Edges: `START -> retrieve`, `retrieve -> grade`, a **conditional** edge from `grade` using `decide_next` with the map `{"answer": "answer", "rewrite": "rewrite", "give_up": "give_up"}`, `rewrite -> retrieve`, `answer -> END`, `give_up -> END`. Return `graph.compile()`.

```python
app.invoke({"question": "refunds", "docs": [], "relevant": [], "tries": 0, "max_tries": 2, "answer": ""})["answer"]
# -> '5 days'    (after one rewrite)
```

**Think first:** what stops this graph from looping forever? (Think of two things: your `max_tries`, and the `recursion_limit` of lesson 8.)

**Hint:** the `give_up` branch is the honest exit. Keep the node names the same as the keys of the map.
