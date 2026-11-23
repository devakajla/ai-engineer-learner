# Supervisor as a LangGraph graph, and handoff with Command

Two ways to wire agents in LangGraph.

**A. Supervisor with a conditional edge.** One node, `supervisor`, picks the next worker. Every worker has an edge **back** to the supervisor. A conditional edge sends control to the chosen worker, or to `END`.

```
START -> supervisor --(name)--> worker -> supervisor ...
                    --(FINISH)--> END
```

**B. Handoff with `Command`.** A node returns `Command(goto="writer", update={...})`. It says "go to this node next, and update the state like this". No edge is needed between the nodes. This is how agents **hand off** to each other without a central boss.

The starter gives you the imports (including `Command`), `ask`, the exercise 1 and 2 functions, and two state shapes: `SupState` (`task`, `results` with an `add` reducer, `next`) and `HandoffState` (`topic`, `notes`, `draft`). Write two builders.

1. `build_supervisor_graph(client, workers, max_steps=4)`:
   - node `"supervisor"`: if `len(state["results"]) >= max_steps` return `{"next": "FINISH"}`. Else `reply = ask(client, supervisor_prompt(state["task"], workers, state["results"]))` and return `{"next": parse_choice(reply, list(workers)) or "FINISH"}` (an unknown name ends the run).
   - one node per worker name: it returns `{"results": [run_worker(client, name, workers[name], state["task"], format_results(state["results"]))]}`. Write a small helper `make_worker_node(name)` that returns the node function (one function for all names, so each node remembers its own `name`).
   - edges: `START -> supervisor`, each worker `-> supervisor`, and a conditional edge from `supervisor` that returns `state["next"]` with the map `{each worker name: same name, "FINISH": END}`.
2. `build_handoff_graph()` (no model): nodes `"researcher"` and `"writer"`, one edge `START -> researcher`.
   - `researcher(state)` returns `Command(goto="writer", update={"notes": "facts about " + state["topic"]})`.
   - `writer(state)` returns `Command(goto=END, update={"draft": "Report: " + state["notes"]})`.

```python
build_handoff_graph().invoke({"topic": "RAG", "notes": "", "draft": ""})
# -> {'topic': 'RAG', 'notes': 'facts about RAG', 'draft': 'Report: facts about RAG'}
```

**Think first:** when is a supervisor better than handoffs, and when are handoffs better?

**Hint:** Python lesson 23 explains the "function that returns a function" shape. If it is new, copy it: `make_worker_node` defines `node` inside and returns it.
