# A graph that chooses

A **conditional edge** lets a function choose the next node. This is the **routing** pattern from lesson 3, now as a graph. The imports and the `RouteState` class are given. Write:

1. `classify(state)`: return `{"route": "math"}` if the question has any digit, otherwise `{"route": "chat"}`.
2. `math_node(state)`: return `{"answer": "math handler: " + state["question"]}`.
3. `chat_node(state)`: return `{"answer": "chat handler: " + state["question"]}`.
4. `pick_route(state)`: return `state["route"]`. This is the function that chooses the edge.
5. `build_router_graph()`: add the three nodes named `"classify"`, `"math"`, `"chat"`. Edges: `START -> classify`. Then `graph.add_conditional_edges("classify", pick_route, {"math": "math", "chat": "chat"})`. Both `math` and `chat` go to `END`. Return `graph.compile()`.

```python
app.invoke({"question": "7 times 8", "route": "", "answer": ""})["answer"]
# -> 'math handler: 7 times 8'
```

**Think first:** the dict `{"math": "math", "chat": "chat"}` maps what to what?

**Hint:** the function returns a label. The dict turns the label into a node name.
