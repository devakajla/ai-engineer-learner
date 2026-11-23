# Your first graph

A LangGraph **graph** has a **state** (a dict that every step can read), **nodes** (functions that do the work) and **edges** (which node runs next). A node gets the whole state and returns **only the keys it wants to change**.

The imports and the `State` class are given. Copy this shape, you will use it in every exercise. `steps: Annotated[list, add]` means that when a node returns `{"steps": ["x"]}`, the value is **appended** to the old list and does not replace it.

Write:

1. `clean(state)`: return `{"text": <state["text"] stripped of spaces at both ends>, "steps": ["clean"]}`.
2. `shout(state)`: return `{"text": <text in upper case> + "!", "steps": ["shout"]}`.
3. `build_linear_graph()`: make `StateGraph(State)`, add the two nodes with `add_node("clean", clean)` and `add_node("shout", shout)`, add edges `START -> clean -> shout -> END` with `add_edge`, and return `graph.compile()`.

```python
app = build_linear_graph()
app.invoke({"text": "  hello ", "steps": []})
# -> {'text': 'HELLO!', 'steps': ['clean', 'shout']}
```

**Think first:** why do the nodes return only the changed keys and not the full state?

**Hint:** `graph.add_edge(START, "clean")` starts the graph. The last edge goes to `END`.
