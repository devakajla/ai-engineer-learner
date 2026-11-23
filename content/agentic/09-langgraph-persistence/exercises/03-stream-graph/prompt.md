# Stream a graph

`invoke` waits for the end. `stream` gives you the results **while the graph runs**. It has modes:

- `stream_mode="updates"`: one item per node, `{node_name: what_it_returned}`. Good for progress ("step 2 of 4").
- `stream_mode="messages"`: the model's text **piece by piece**, as `(chunk, metadata)` pairs. Good for a chat screen that types the answer. `metadata["langgraph_node"]` tells which node made the chunk.

The imports and the code from exercise 2 (`build_graph`, `build_memory_chat`) are given. Write:

1. `stream_nodes(app, state, config=None)`: run `app.stream(state, config, stream_mode="updates")` and return the list of **node names** in order. Each update is a dict with one key: the node name.
2. `stream_reply(app, thread_id, text)`: stream `{"messages": [HumanMessage(text)]}` with the thread config and `stream_mode="messages"`. For each `(chunk, meta)` where `meta["langgraph_node"] == "model"`, collect `chunk.content`. Return all pieces joined into one string.

```python
stream_nodes(app, {"n": 1, "log": []})
# -> ['one', 'two']
stream_reply(app, "t1", "hi")
# -> 'Hello Dev'   (it arrived in many small pieces)
```

**Think first:** a chat page wants to show words as they arrive. Which mode do you use?

**Hint:** use `meta.get("langgraph_node")` so a missing key does not crash.
