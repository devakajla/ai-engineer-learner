# A graph with a loop

An edge can point **back** to an earlier node, so a graph can loop. This is how agents loop in LangGraph. Every loop needs a way out, so you also add a limit. This is the evaluator-optimizer idea from lesson 3.

The imports and the `LoopState` class are given. Write `build_retry_graph(try_once, max_tries)`. `try_once(n)` is a function you are given. It takes the try number (1, 2, 3, ...) and returns `True` or `False`.

1. Inside, define a node `attempt(state)`: `tries = state["tries"] + 1`, `ok = try_once(tries)`. Return `{"tries": tries, "ok": ok, "log": [f"try {tries}: ok"]}`, where the log text says `ok` when `ok` is true and `fail` otherwise.
2. Define `should_stop(state)`: return `"stop"` if `state["ok"]` is true **or** `state["tries"] >= max_tries`, otherwise `"again"`.
3. Make the graph: node `"attempt"`, edge `START -> attempt`, and `add_conditional_edges("attempt", should_stop, {"again": "attempt", "stop": END})`. Return `graph.compile()`.

```python
app = build_retry_graph(lambda n: n >= 3, 5)
app.invoke({"tries": 0, "ok": False, "log": []})
# -> {'tries': 3, 'ok': True, 'log': ['try 1: fail', 'try 2: fail', 'try 3: ok']}
```

**Think first:** what would happen without `max_tries` if `try_once` never returns `True`?

**Hint:** the node and the two small functions can live inside `build_retry_graph`, so they can see `try_once` and `max_tries`.
