---
title: "LangGraph: checkpointer, persistence, streaming and time travel"
summary: Give a graph a memory with a checkpointer and thread ids, read and delete saved state, stream progress and text, and travel back in time to debug or fork a run.
plan_ids: []
---

A graph from lesson 8 forgets everything when a run ends. A chat bot must remember the conversation. A long job must survive a crash. A person may close the browser and come back tomorrow.

All of these need **saved state**. LangGraph saves it for you with a **checkpointer**. Once the state is saved after every step, you also get three more things almost for free: streaming, resuming after a pause (lesson 10) and **time travel**.

## Checkpointer and thread id

A **checkpoint** is a snapshot of the state after a step. A **checkpointer** is the thing that stores the snapshots. A **thread** is one conversation or one job. You name it with a **`thread_id`**.

```python
from langgraph.checkpoint.memory import InMemorySaver

app = graph.compile(checkpointer=InMemorySaver())
config = {"configurable": {"thread_id": "dev-1"}}

app.invoke({"messages": [HumanMessage("I am Dev")]}, config)
app.invoke({"messages": [HumanMessage("Who am I?")]}, config)   # the model sees both turns
```

What just happened:

1. `compile(checkpointer=...)` tells the app to save after each step.
2. The config carries the `thread_id`. Same id means the same conversation. A new id means a clean start.
3. On the second call you send **only the new message**. LangGraph loads the saved state, the `add_messages` reducer adds your message to it, and the model sees the whole history.

Compare this with GenAI lesson 12, where you stored the list and passed it back by hand. Here the framework does it.

> **Which saver?** `InMemorySaver` lives in RAM and is gone when the program stops. Use it in tests and demos. For real apps use a database saver: SQLite or Postgres (separate packages such as `langgraph-checkpoint-sqlite` and `langgraph-checkpoint-postgres`; check the docs for the current names). The code of your graph does not change. Only the `checkpointer=` line does.

### Step by step: a chat with memory (exercise 1)

1. Write the chat graph as in lesson 8, but do not compile it yet.
2. Compile it with `checkpointer=InMemorySaver()`.
3. Write `chat(app, thread_id, text)`: put the thread id in the config, send only the new message, return the last message's text.
4. Test it: two calls on one thread, and one call on another thread. The second thread must not know the first.

## Read and delete saved state

```python
snapshot = app.get_state(config)
print([m.type for m in snapshot.values["messages"]])
# -> ['human', 'ai', 'human', 'ai']
print(snapshot.next)
# -> ()      (nothing waits; the run is finished)
```

`get_state` returns a **snapshot**. `.values` is the state dict. `.next` is the tuple of nodes that would run next (empty when finished; not empty when the run is paused, see lesson 10).

To delete a thread: `app.checkpointer.delete_thread("dev-1")`. This matters for privacy. A saved chat is personal data, so give users a way to erase it.

## Streaming

`invoke` waits for the end. `stream` lets you show progress. The `stream_mode` picks what you get:

| Mode | You get | Use it for |
|---|---|---|
| `"values"` | the full state after each step | simple debugging |
| `"updates"` | `{node: returned_update}` after each node | progress bars, logs |
| `"messages"` | model text piece by piece, with metadata | a chat that types the answer |
| `"custom"` | anything your node sends with a writer | custom events |

```python
for update in app.stream({"n": 1, "log": []}, stream_mode="updates"):
    print(update)
# -> {'inc': {'n': 2, 'log': ['inc']}}
# -> {'double': {'n': 4, 'log': ['double']}}
```

```python
for chunk, meta in app.stream(inputs, config, stream_mode="messages"):
    print(chunk.content, end="")      # pieces of the answer
```

In `"messages"` mode each item is a pair: the chunk and a metadata dict. `meta["langgraph_node"]` is the node that made the chunk. You use this to show only the answer of the node you want. A web server sends these pieces to the browser with SSE (GenAI lesson 28).

### Step by step: collect streamed text (exercise 3)

1. Loop over `app.stream(..., stream_mode="messages")`.
2. Each item is `(chunk, meta)`. Skip the ones from other nodes with `meta.get("langgraph_node")`.
3. Add `chunk.content` to a list.
4. Join the list into one string at the end.

## Time travel

Every checkpoint is kept. `get_state_history(config)` lists them, **newest first**:

```python
for snap in app.get_state_history(config):
    print(snap.metadata["step"], snap.next, snap.values)
# -> 2 ()           {'n': 4, 'log': ['inc', 'double']}
# -> 1 ('double',)  {'n': 2, 'log': ['inc']}
# -> 0 ('inc',)     {'n': 1, 'log': []}
# -> -1 ('__start__',) {'log': []}
```

Each snapshot has a `config` that points at that checkpoint. You can use it in two ways:

- **Replay:** `app.invoke(None, snap.config)`. Passing `None` as the input means "continue from here". The nodes after that checkpoint run again. This is useful to retry after you fixed a bug.
- **Fork:** `forked = app.update_state(snap.config, {"n": 10})` writes a changed state as a **new** checkpoint, then `app.invoke(None, forked)` runs forward from it. The old history stays. A fork starts a new branch.

Why is this useful for agents? When an agent made a bad choice at step 5, you can go back to step 5, change what the model saw (or the tool result), and run again, without paying for steps 1 to 4. It is like a debugger that can step back.

## Try it live

1. Build the memory chat with `ChatGroq`. Tell it your name on thread `a`, then ask "what is my name?" on thread `a` and on thread `b`.
2. Print `app.get_state(config).values["messages"]` after three turns.
3. Stream with `stream_mode="messages"` and print the pieces with `end=""`. Watch the text arrive.
4. Print the history of a thread. Replay from step 1. Then fork with a different user message.
5. Delete the thread and call `get_state` again.

## A little deeper

- **Super-steps.** LangGraph runs in rounds. All nodes that can run at the same time form one round (a super-step), and one checkpoint is saved per round.
- **Long-term memory is different.** A checkpointer keeps one thread. Facts that should last across threads ("the user likes Python") go in a **store**. You build that idea in lesson 11.
- **Resume after a crash.** Because the state is saved, you can call `invoke(None, config)` after a restart and the run continues from the last checkpoint.
- **State grows.** The `messages` list grows with every turn and so does the token cost. Trim or summarise it (lesson 11).
- **Serialisation.** State must be something the saver can store (strings, numbers, lists, dicts, messages). Do not put open files or database connections in it.

## Common mistakes

- Forgetting the `thread_id` in the config. A checkpointer needs it, and LangGraph raises an error.
- Re-sending the whole history on every call. Send only the new message, the saver adds it.
- Using `InMemorySaver` in production. A restart loses everything.
- Using one `thread_id` for all users. Everybody then shares one conversation. Make it unique per user and conversation.
- Never deleting threads that hold personal data.
- Confusing a **thread** (one conversation) with **long-term memory** (facts across conversations).

## Interview corner

**What is a checkpointer and what does it give you?**
It saves the state after each step. You get memory across calls (with a `thread_id`), resume after a pause or crash, human-in-the-loop, and time travel.

**What is a `thread_id`?**
The key of one conversation or job. Same id continues the same state. Different ids are independent.

**How do you show progress or stream text?**
`app.stream(...)` with a mode: `updates` for node progress, `messages` for model tokens, `values` for the full state.

**What is time travel?**
Reading the checkpoint history, going back to a step, and either replaying from there or forking with changed state. It is a way to debug and to retry without redoing earlier steps.

**Short-term vs long-term memory?**
Short-term is the state of one thread (saved by the checkpointer). Long-term is shared across threads, kept in a store, and holds facts that should last.

## Summary

- `compile(checkpointer=...)` saves state after each step. Pass a `thread_id` in the config. Send only the new input.
- `InMemorySaver` is for tests. Use a database saver in production. Delete threads on request.
- `get_state(config)` reads the state (`.values`, `.next`).
- `stream` modes: `updates` (per node), `messages` (model text pieces), `values` (full state).
- `get_state_history` lists checkpoints, newest first. `invoke(None, config)` replays. `update_state` plus `invoke(None, ...)` forks.
- Short-term memory is one thread. Long-term memory is a store (lesson 11).
- Reference: `reference/agentic-langchain-langgraph.md`.
