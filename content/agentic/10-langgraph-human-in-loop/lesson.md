---
title: "LangGraph: human-in-the-loop, interrupts, parallel branches and subgraphs"
summary: Pause a graph to ask a person, resume it with their answer, run branches at the same time with fan-out and Send, and split a big graph into subgraphs.
plan_ids: []
---

You can now build graphs that remember (lesson 9). Real agents also need to **stop and ask**, to **do work at the same time**, and to stay **readable** when they grow. This lesson covers those three things.

- **Human-in-the-loop:** an agent must not send money or delete data without a yes from a person.
- **Parallel branches:** independent work (three searches, ten documents) should not run one after another.
- **Subgraphs:** one big graph of 30 nodes is hard to read. Several small graphs are easier.

## Human-in-the-loop with `interrupt`

A node can call `interrupt(value)`. This does two things:

1. It **stops** the run at that point. The state is saved by the checkpointer. The `value` is handed to you, the caller.
2. Later, when you **resume**, `interrupt(...)` returns the answer you give, and the node continues.

```python
from langgraph.types import Command, interrupt

def ask_human(state):
    answer = interrupt({"question": f"Approve: {state['request']}?"})
    return {"approved": answer == "yes"}
```

The first call stops:

```python
config = {"configurable": {"thread_id": "t1"}}
result = app.invoke({"request": "pay 100", "approved": False, "result": ""}, config)
print(result["__interrupt__"][0].value)
# -> {'question': 'Approve: pay 100?'}
print(app.get_state(config).next)
# -> ('ask_human',)
```

`"__interrupt__"` holds the question. `get_state(config).next` shows which node is waiting. Nothing after that node has run.

Then you resume, maybe hours later, maybe after a server restart:

```python
out = app.invoke(Command(resume="yes"), config)
print(out["result"])
# -> done: pay 100
```

What just happened: `Command(resume="yes")` told LangGraph to continue thread `t1`. It re-entered `ask_human`, and `interrupt(...)` returned `"yes"` this time.

> **Two rules.** (1) You **need a checkpointer** and a `thread_id`. Without them there is nothing to resume from. (2) The node **starts again from its first line** when you resume. So code before `interrupt` runs twice. Keep that code free of side effects (no emails, no payments before the question).

### Step by step: an approval graph (exercise 1)

1. State: the request, an `approved` flag, a `result`.
2. Node `ask_human`: call `interrupt` with a question, return `approved` from the answer.
3. A router function reads `approved` and picks `run` or `cancel`.
4. Two action nodes write the result.
5. Compile with a checkpointer.
6. Two helpers: `start` (invoke, return the question) and `answer` (invoke with `Command(resume=...)`).

### More than yes or no

The resume value can be any data. A common pattern is **approve, edit or reject**:

```python
review = interrupt({"draft": state["draft"], "options": ["approve", "edit", "reject"]})
# resume with: Command(resume={"action": "edit", "text": "Hello Sam"})
```

Keep the logic that reads the review in a small plain function (exercise 2). Then you can test it without a graph.

**Where to put the gate.** For agents with tools, a good place is a node **before** the tool node. It looks at the tool calls and asks a person only for the risky ones (sending, paying, deleting). Safe, read-only calls pass without a pause. You design this "risk tier" in lesson 15.

## Parallel branches

Two kinds:

**1. Fixed fan-out.** Give a node two outgoing edges and both targets run in the same step. If they both point to one node, that node waits for **both** and runs once:

```python
graph.add_edge(START, "count_words")
graph.add_edge(START, "count_chars")
graph.add_edge("count_words", "report")
graph.add_edge("count_chars", "report")
```

The two counters run together, then `report` sees both results.

**2. Map-reduce with `Send`.** When the **number** of branches is only known at run time (one per document, one per subtask), a routing function returns a list of `Send` objects:

```python
from langgraph.types import Send

def fan_out(state):
    return [Send("worker", {"item": item}) for item in state["items"]]

graph.add_conditional_edges(START, fan_out, ["worker"])
```

Each `Send` starts one copy of `worker` with its **own small input**. The results flow back into a shared key that has a **reducer**:

```python
results: Annotated[list, add]
# worker returns {"results": [one_result]}; all of them are appended
```

Then a `combine` node reads the full list. This is the **orchestrator-workers** pattern of lesson 3, now with real parallel runs. In exercise 3 you build both kinds.

> **Why a reducer is a must here.** When two branches write the same key in the same step, LangGraph needs a rule to combine the values. Without a reducer you get an error.

## Subgraphs

A compiled graph can be a node in another graph:

```python
parent.add_node("clean", clean_subgraph)      # clean_subgraph = sub.compile()
```

If parent and child **share state keys**, you add the compiled child directly, as above. If their states are different, wrap it in a function: the function turns the parent state into the child input, calls `child.invoke(...)`, and turns the result back into an update.

A subgraph is **one node** from the parent's point of view. This keeps the top graph short: `understand -> research -> write -> review`. Each box can be its own small, tested graph. Multi-agent systems (lesson 13) use this idea heavily.

### Step by step: a subgraph (exercise 4)

1. Build and compile a small graph (strip, then lower-case) that works alone. Test it alone.
2. Build the parent graph. Use the compiled child as one of its nodes.
3. Add the other parent nodes and the edges.
4. Stream it: you see `clean` as one update, not two.

## Try it live

1. Build the approval graph around a **real** tool: `send_email(to, body)` that only prints. Interrupt before it. Resume once with `"yes"` and once with `"no"`.
2. Stop your program while the graph is paused, start it again with a database checkpointer and resume. (Use `InMemorySaver` first. It cannot survive a restart, which proves why you need the other kind.)
3. Fan out over 5 short texts with `Send`, and summarise each with a real model. Time it against a loop.
4. Draw your parent graph with `get_graph().draw_mermaid()`. Add `xray=True` to see inside the subgraphs: `get_graph(xray=True)`.

## A little deeper

- **Several interrupts.** A node can call `interrupt` more than once. They are matched to resume values in order. When two parallel nodes interrupt, you can resume them together with a dict of ids.
- **Static breakpoints.** You can also compile with `interrupt_before=["tools"]` to always pause before a node, with no code in the node. `interrupt()` inside the node is more flexible, because it can decide and can carry data.
- **Timeouts.** A paused thread can wait for days. Add your own expiry: a job that cancels threads that waited too long.
- **Resume can also edit state.** Use `update_state` (lesson 9) to change the state while paused, then resume.
- **Concurrency limit.** Many `Send` branches at once can hit rate limits. Use `max_concurrency` in the run config.

## Common mistakes

- Using `interrupt` with no checkpointer.
- Doing side effects (send, pay, write) before `interrupt` in the same node. They run again on resume.
- Resuming with the wrong `thread_id`.
- Two parallel branches writing one key with no reducer.
- Asking a person about **every** tool call. They will click "yes" without reading. Ask only for risky ones.
- Treating a subgraph as a function with different state keys and wondering why nothing changes.

## Interview corner

**How do you add a human approval step in LangGraph?**
Call `interrupt(payload)` in a node (or compile with `interrupt_before`). The run stops and the state is saved. Resume with `Command(resume=answer)` on the same `thread_id`. A checkpointer is required.

**Why must code before `interrupt` have no side effects?**
When you resume, the node runs again from the beginning. Anything before the `interrupt` call runs a second time.

**How do you run steps in parallel?**
Fan out with two edges from one node (they join where both point to the same node), or use `Send` for a run-time number of branches. Use a reducer for any key that parallel branches write.

**What is a subgraph and when do you use one?**
A compiled graph used as a node of another graph. Use it to keep graphs small, to test parts alone, and to build multi-agent systems.

**Which actions should need human approval?**
Actions that cannot be undone or that cost money or touch other people: payments, deletes, emails, deployments. Read-only steps should not.

## Summary

- `interrupt(value)` pauses a node and saves the state. `Command(resume=answer)` continues it. You need a checkpointer and a `thread_id`.
- The node restarts from its first line on resume, so no side effects before `interrupt`.
- The resume value can be any data: yes/no, or approve/edit/reject.
- Fan-out edges run nodes together and join where they meet. `Send` makes a run-time number of branches. Parallel writes need a **reducer**.
- A compiled graph can be a node (a **subgraph**). It is one step for the parent.
- Ask a human only for risky actions.
- Reference: `reference/agentic-langchain-langgraph.md`.
