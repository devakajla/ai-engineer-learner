# The standard chat graph

Almost every LangGraph agent has a state with a `messages` list. The reducer `add_messages` **adds** new messages to the list (it never replaces it). The imports and the `ChatState` class are given.

Write `build_chat_graph(model)`:

1. Inside, define a node `call_model(state)`: call `model.invoke(state["messages"])` and return `{"messages": [reply]}`. (Return a list with one message. The reducer adds it.)
2. Make `StateGraph(ChatState)`, add the node `"model"`, and add the edges `START -> model -> END`.
3. Return `graph.compile()`.

```python
app = build_chat_graph(model)
out = app.invoke({"messages": [HumanMessage("hello")]})
[m.type for m in out["messages"]]
# -> ['human', 'ai']
```

**Think first:** what would go wrong if the node returned `{"messages": reply}` instead of a list?

**Hint:** the model comes from the function's argument, so define `call_model` inside `build_chat_graph`.
