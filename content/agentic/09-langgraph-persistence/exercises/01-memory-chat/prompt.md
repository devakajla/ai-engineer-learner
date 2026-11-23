# Give the graph a memory

In lesson 8 a graph forgot everything after each run. A **checkpointer** saves the state after every step. You pass a **`thread_id`** with each call, and calls with the same id continue the same conversation. In GenAI lesson 12 you kept memory by hand. Here LangGraph does it.

The imports, the `ChatState` class and `build_graph(model)` (an **uncompiled** chat graph) are given. Write:

1. `build_memory_chat(model)`: return `build_graph(model).compile(checkpointer=InMemorySaver())`.
2. `chat(app, thread_id, text)`: call the app with `{"messages": [HumanMessage(text)]}` and the config `{"configurable": {"thread_id": thread_id}}`. Return the text (`.content`) of the **last** message in the result.

```python
app = build_memory_chat(model)
chat(app, "t1", "I am Dev")      # -> 'Hello Dev'
chat(app, "t1", "Who am I?")     # the model sees all 3 messages
chat(app, "t2", "Who am I?")     # a new thread: the model sees 1 message
```

**Think first:** you send only the **new** message each time. Where do the old messages come from?

**Hint:** the checkpointer is an argument of `compile`, not of `invoke`.
