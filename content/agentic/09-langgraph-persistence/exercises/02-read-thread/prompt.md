# Read and clear a thread

The checkpointer stores the state of every thread. You can read it with `app.get_state(config)`. Its `.values` is the state dict (it can be empty for a new thread, so use `.get`). The imports and the code from exercise 1 are given.

Write three functions. For all of them `config` is `{"configurable": {"thread_id": thread_id}}`.

1. `thread_messages(app, thread_id)`: return the messages of the thread as strings `"<type>: <content>"`, for example `"human: hi"` and `"ai: Hello"`. A message has `.type` and `.content`. A new thread gives `[]`.
2. `thread_count(app, thread_id)`: how many messages are in the thread.
3. `forget_thread(app, thread_id)`: delete the thread with `app.checkpointer.delete_thread(thread_id)`. This is how you honour "delete my data".

```python
thread_messages(app, "t1")
# -> ['human: I am Dev', 'ai: Hello Dev']
```

**Think first:** why is a saved conversation something you must be able to delete?

**Hint:** `app.get_state(config).values` is a dict. `.get("messages", [])` is safe for an empty thread.
