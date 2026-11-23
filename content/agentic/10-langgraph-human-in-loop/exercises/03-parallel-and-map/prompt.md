# Run branches at the same time

Two ways to run work in parallel in LangGraph:

- **Fan-out with edges.** Give one node two outgoing edges. Both targets run in the same step. If both then have an edge to the same node, that node runs **once, after both** are done.
- **`Send` (map-reduce).** A conditional edge function returns a list of `Send("worker", {"item": x})`, one for each item. Each `Send` starts one copy of the worker with its own small state. The workers' results are collected by a **reducer** (here `add`), then a `combine` node uses them. The number of workers is decided at run time. This is the orchestrator-workers idea from lesson 3.

The imports and the two state classes are given. Write:

1. `build_parallel_graph()` with `ParallelState`. Nodes (use lambdas or small functions):
   - `"count_words"` returns `{"words": len(state["text"].split())}`
   - `"count_chars"` returns `{"chars": len(state["text"])}`
   - `"report"` returns `{"report": f"{words} words, {chars} chars"}` (read `words` and `chars` from the state)
   Edges: `START -> count_words`, `START -> count_chars`, `count_words -> report`, `count_chars -> report`, `report -> END`.
2. `build_map_graph(work)` with `MapState`. `work(item)` is a function you are given.
   - `fan_out(state)` returns `[Send("worker", {"item": item}) for item in state["items"]]`.
   - `worker(state)` returns `{"results": [work(state["item"])]}`.
   - `combine(state)` returns `{"total": sum(state["results"])}`.
   - Nodes `"worker"` and `"combine"`. Edges: `graph.add_conditional_edges(START, fan_out, ["worker"])`, `worker -> combine`, `combine -> END`.

```python
build_parallel_graph().invoke({"text": "hello big world", "words": 0, "chars": 0, "report": ""})["report"]
# -> '3 words, 15 chars'
build_map_graph(lambda x: x * x).invoke({"items": [1, 2, 3], "results": [], "total": 0})["total"]
# -> 14
```

**Think first:** why must `results` have a reducer? What if two workers finish at the same time?

**Hint:** the third argument of `add_conditional_edges` (`["worker"]`) lists the nodes the function may send to.
