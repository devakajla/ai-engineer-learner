# One safe tool call, all the checks together

Now combine the pieces into the function that sits between the model and your tools. The model asks for a call. This function decides what actually happens, and keeps a record.

The starter gives you `scan_tool_output`, `quarantine` (exercise 1), `tool_risk` and `needs_approval` (exercise 2). Write `run_tool_safely(call, registry, table, approve, audit, limits=None)`:

- `call` is `{"name": ..., "args": {...}}` (`args` may be missing: use `{}`).
- `registry` maps tool names to Python functions. `approve(name, args)` is a function that returns `True` or `False` (in real life it asks a person). `audit` is a list you append to.

Steps, in order:

1. Unknown tool (not in `registry`): append `{"tool": name, "args": args, "decision": "unknown", "flags": []}` to `audit` and return `f"Error: unknown tool {name}"`.
2. If `needs_approval(name, args, table, limits)`: call `approve(name, args)`. If it says no, append the same kind of entry with `"decision": "denied"` and return `"DENIED: a person did not approve this call"`. If yes, the decision is `"approved"`. Without the need, the decision is `"ran"`.
3. Run the tool: `raw = str(registry[name](**args))`. If it raises, `raw = f"Error: {error}"`.
4. `result = quarantine(name, raw)`. Append `{"tool": name, "args": args, "decision": decision, "flags": result["flags"]}` to `audit`.
5. Return `result["text"]`.

```python
run_tool_safely({"name": "search", "args": {"query": "rag"}}, registry, table, approve, audit)
# -> '<tool_output name="search" trust="untrusted">\nresult for rag\n</tool_output>'
```

**Think first:** why is the audit log written for denied and unknown calls too?

**Hint:** build `args = call.get("args", {})` once at the top.
