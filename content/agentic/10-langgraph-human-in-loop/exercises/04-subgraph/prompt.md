# A graph inside a graph

A compiled graph can be a **node** of another graph. This is a **subgraph**. Use it to keep a big flow readable: one team owns the "clean text" graph, another owns the "answer" graph, and a parent graph joins them. If the parent and the child **share state keys** (here `text` and `log`), you can add the compiled child directly with `add_node("name", child_app)`.

The imports and the `PipeState` class are given. Write:

1. `build_clean_subgraph()`: a graph over `PipeState` with two nodes. `"strip"` returns `{"text": state["text"].strip()}` and `"lower"` returns `{"text": state["text"].lower()}`. Edges `START -> strip -> lower -> END`. Return `sub.compile()`.
2. `build_pipeline()`: a parent graph over `PipeState` with three nodes:
   - `"clean"`: the **compiled subgraph** from step 1 (not a function).
   - `"tag"`: returns `{"log": state["log"] + ["cleaned"]}`.
   - `"finish"`: returns `{"text": state["text"] + "!", "log": state["log"] + ["finished"]}`.
   Edges `START -> clean -> tag -> finish -> END`. Return `parent.compile()`.

```python
build_pipeline().invoke({"text": "  HeLLo  ", "log": []})
# -> {'text': 'hello!', 'log': ['cleaned', 'finished']}
```

**Think first:** from the parent's point of view, how many steps is the subgraph?

**Hint:** `parent.add_node("clean", build_clean_subgraph())`. No function wrapper is needed.
