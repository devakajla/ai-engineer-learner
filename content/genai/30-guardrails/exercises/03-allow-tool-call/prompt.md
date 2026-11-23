# Least privilege for tools

An agent should only be able to do what it **needs**. Two rules:
- **Allow-list**: only tools on the list may run, even if the model asks for another name.
- **Human approval** for risky tools (delete, pay, send email): a person must say yes first.

Write `allow_tool_call(name, args, allowed, risky, approve)`.

- `allowed`: a list of tool names the agent may use.
- `risky`: a list of tool names that need approval (they should also be in `allowed`).
- `approve(name, args)`: a function that asks a human and returns `True` or `False`. It is passed in, so tests can fake it.

Rules:
1. `name` not in `allowed`: return `{"ok": False, "reason": "tool not allowed"}`. Do **not** call `approve`.
2. `name` in `risky`: call `approve(name, args)`. If it returns false, return `{"ok": False, "reason": "not approved"}`.
3. Otherwise return `{"ok": True, "reason": ""}`. Safe tools must **not** call `approve`.

```python
allow_tool_call("search", {}, ["search", "refund"], ["refund"], approve)       # -> {'ok': True, 'reason': ''}   (approve not asked)
allow_tool_call("refund", {"id": 7}, ["search", "refund"], ["refund"], approve)  # asks approve("refund", {"id": 7})
allow_tool_call("drop_db", {}, ["search"], [], approve)                        # -> {'ok': False, 'reason': 'tool not allowed'}
```

**Think first:** the model decides the arguments. Why is an allow-list on the **name** alone not enough for a `send_email` tool?
