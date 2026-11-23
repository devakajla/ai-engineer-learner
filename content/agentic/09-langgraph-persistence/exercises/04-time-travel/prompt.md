# Time travel

Because the checkpointer saves the state after **every** step, you can look at the history of a thread, go back to any step and run again from there. You can even **change** the state at that step and go forward on a new branch (a "fork"). This is called **time travel**. It is very useful to debug an agent: "what if the model had seen this instead?"

The imports and `build_counter()` (a small graph with a checkpointer: `inc`, then `double`) are given. Every snapshot from `app.get_state_history(config)` has `.metadata["step"]` (the step number, starting at -1), `.next` (the nodes that run next), `.values` (the state) and `.config` (a config that points at that checkpoint). The history comes **newest first**.

Write four functions. `config` is `{"configurable": {"thread_id": thread_id}}`:

1. `list_checkpoints(app, thread_id)`: a list with one dict per snapshot, **oldest first**: `{"step": ..., "next": list(snapshot.next), "values": snapshot.values}`.
2. `find_checkpoint(app, thread_id, step)`: return the `.config` of the snapshot with this step, or `None` if there is none.
3. `replay_from(app, thread_id, step)`: run the graph again from that checkpoint: `app.invoke(None, checkpoint_config)`. Passing `None` as the input means "just continue". Return the result.
4. `fork_from(app, thread_id, step, changes)`: `forked = app.update_state(checkpoint_config, changes)` makes a new checkpoint with the changes. Then `app.invoke(None, forked)` and return the result.

```python
app.invoke({"n": 1, "log": []}, config)       # inc -> 2, double -> 4
fork_from(app, "t", 1, {"n": 10})              # at step 1 set n = 10, then `double` runs
# -> {'n': 20, 'log': ['inc', 'double']}
```

**Think first:** if you replay from step 1, which nodes run again?

**Hint:** `list(app.get_state_history(config))` gives snapshots newest first. Use `.reverse()` for the oldest-first list.
