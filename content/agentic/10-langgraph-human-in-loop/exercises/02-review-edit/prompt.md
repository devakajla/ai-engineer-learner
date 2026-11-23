# Approve, edit or reject

A human often wants more than yes or no. They want to **edit** the draft. The value you pass to `Command(resume=...)` can be any data (a dict, for example), and `interrupt(...)` returns exactly that. The imports are given.

Write:

1. `apply_review(draft, review)` (a plain function, easy to test). `review` is a dict with an `"action"`:
   - `"approve"`: return the draft.
   - `"edit"`: return `review["text"]` (if there is no `"text"` key, return the draft).
   - anything else (including a missing action): return `None`.
2. `review_node(state)`: `review = interrupt({"draft": state["draft"], "options": ["approve", "edit", "reject"]})`, then `final = apply_review(state["draft"], review)`. Return `{"final": final}`, or `{"final": "REJECTED"}` when `final` is `None`.
3. `build_review_graph()`: node `"review"`, edges `START -> review -> END`, compiled with `checkpointer=InMemorySaver()`.

The `ReviewState` class (fields `draft` and `final`) is given. A paused run returns `"__interrupt__"`, as in exercise 1.

```python
app.invoke({"draft": "Dear Sam", "final": ""}, config)       # pauses
app.invoke(Command(resume={"action": "edit", "text": "Hi Sam"}), config)["final"]
# -> 'Hi Sam'
```

**Think first:** why keep `apply_review` as a separate small function and not put the `if`s inside the node?

**Hint:** `None` means "no usable review". Check `is None`, because an empty string is a valid edit.
