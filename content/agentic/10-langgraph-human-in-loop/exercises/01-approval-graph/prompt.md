# Pause for a human

Some actions must not run without a person saying yes: sending money, deleting data, emailing a customer. In LangGraph a node can call **`interrupt(value)`**. The run **stops there** and the state is saved by the checkpointer. Later you continue with `Command(resume=answer)`. The `interrupt(...)` call then **returns the answer**, and the node goes on.

The imports and the `ApprovalState` class are given. A paused `invoke` returns the state plus a key `"__interrupt__"`: a list of interrupts, each with a `.value` (what you passed to `interrupt`). The graph needs a checkpointer, or there is nothing to resume from.

Write these functions:

1. `ask_human(state)`: `answer = interrupt({"question": f"Approve: {state['request']}?"})`, then return `{"approved": answer == "yes"}`.
2. `choose(state)`: return `"run"` if `state["approved"]`, else `"cancel"`.
3. `run_it(state)`: return `{"result": "done: " + state["request"]}`. `cancel_it(state)`: return `{"result": "cancelled: " + state["request"]}`.
4. `build_approval_graph()`: nodes `"ask_human"`, `"run"` (run_it), `"cancel"` (cancel_it). Edges: `START -> ask_human`, a conditional edge from `ask_human` using `choose`, and both `run` and `cancel` go to `END`. Compile with `checkpointer=InMemorySaver()`.
5. `start_request(app, thread_id, request)`: invoke with `{"request": request, "approved": False, "result": ""}` and the thread config. Return the question text: `result["__interrupt__"][0].value["question"]`.
6. `answer_request(app, thread_id, answer)`: invoke with `Command(resume=answer)` and the same config. Return the result.

```python
start_request(app, "t1", "pay 100")     # -> 'Approve: pay 100?'
answer_request(app, "t1", "yes")["result"]
# -> 'done: pay 100'
```

**Think first:** the node runs **again from its start** when you resume. Why should the code before `interrupt` have no side effects?

**Hint:** only the exact answer `"yes"` approves. Everything else cancels.
