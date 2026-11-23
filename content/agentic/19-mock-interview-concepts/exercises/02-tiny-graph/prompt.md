# Interview drill 2: a tiny LangGraph

**Asked as:** "Without a library, how would you implement a graph runner with conditional edges and a loop limit?"

Model:

- `nodes`: a dict `{name: function(state) -> dict of updates}`.
- `edges`: a dict `{name: target}`. The target is either a node name (a string) or a **function** `function(state) -> node name` (a conditional edge). A node that is not in `edges` goes to `"END"`.
- The run starts at `start` and stops when the next node is `"END"`.

Write:

1. `next_node(edges, node, state)`: look up `edges.get(node, "END")`. If it is callable, call it with `state`. Return the node name.
2. `run_graph(nodes, edges, start, state, max_steps=20)`: loop: add the node name to `path`; if `len(path) > max_steps` raise `RuntimeError("recursion limit reached")`; run the node and apply its update with `state.update(...)`; pick the next node with `next_node`. Return `{"state": state, "path": path}`.

```python
nodes = {"work": lambda s: {"n": s["n"] + 1}}
edges = {"work": lambda s: "work" if s["n"] < 3 else "END"}
run_graph(nodes, edges, "work", {"n": 0})
# -> {'state': {'n': 3}, 'path': ['work', 'work', 'work']}
```

**Think first:** which part of real LangGraph does `max_steps` correspond to?

**Hint:** `callable(target)` tells a function from a string. Check the limit **before** running the node.
