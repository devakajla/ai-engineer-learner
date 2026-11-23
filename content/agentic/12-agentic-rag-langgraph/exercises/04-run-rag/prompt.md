# Run it and show the path

An agent that decides things must be **inspectable**. Which steps ran? How many searches did it need? If the answer is bad, this tells you where to look. In lesson 9 you saw `stream_mode="updates"`: it gives one `{node_name: update}` item per node that ran.

The starter gives you everything from exercise 3, including `build_rag_graph`. Write `run_rag(app, question, max_tries=2)`:

1. Make the start state: `{"question": question, "docs": [], "relevant": [], "tries": 0, "max_tries": max_tries, "answer": ""}`.
2. Loop over `app.stream(state, stream_mode="updates")`. Each item is a dict with one key (the node name) and the update dict as value.
3. Collect the node names, in order, in a list `path`. When an update contains an `"answer"` key, remember its value.
4. Return `{"answer": answer, "tries": path.count("retrieve"), "path": path}`.

```python
run_rag(app, "refunds")
# -> {'answer': '5 days', 'tries': 2,
#     'path': ['retrieve', 'grade', 'rewrite', 'retrieve', 'grade', 'answer']}
```

**Think first:** what would you log in production from this result? (The number of tries is a cost signal. A path ending in `give_up` is a quality signal.)

**Hint:** `for node, change in update.items():` inside the loop.
