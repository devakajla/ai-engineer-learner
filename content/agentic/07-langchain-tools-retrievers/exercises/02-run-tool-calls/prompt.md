# Run the tool calls of a model message

When a model wants a tool, its `AIMessage` has a list `tool_calls`. Each call is a dict: `{"name": ..., "args": {...}, "id": ...}`. Your code must run each one and answer with a `ToolMessage` that has the **same id**. This is the "act" half of the agent loop from GenAI lesson 27, in LangChain form.

The imports and the tool `convert_temp` are given. Write `run_tool_calls(ai_message, tools)`:

1. Build a dict from tool name to tool.
2. For each call in `ai_message.tool_calls`, in order, make a `ToolMessage(content=..., tool_call_id=call["id"])`:
   - the tool name is unknown: content `f"Error: unknown tool {name}"`.
   - the tool runs: content is `str(tool.invoke(call["args"]))`.
   - the tool raises an error: content `f"Error: {error}"`. One failing call must not stop the others.
3. Return the list of `ToolMessage`s (an empty list when there are no calls).

```python
run_tool_calls(ai_message, [convert_temp])
# -> [ToolMessage(content='212.0', tool_call_id='c1')]
```

**Think first:** why return an error as a message instead of raising it?

**Hint:** `try` / `except Exception as error` around `tool.invoke`.
