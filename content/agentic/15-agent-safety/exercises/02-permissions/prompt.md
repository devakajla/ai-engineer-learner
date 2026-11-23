# Least privilege and approval tiers

Two rules keep agents safe:

- **Least privilege:** an agent gets only the tools its job needs. A support agent has no `delete_file`.
- **Risk tiers:** each tool is `"low"` (read-only), `"medium"` (has effects, but small) or `"high"` (hard to undo). High-risk calls need a human **yes** (lesson 10). Medium calls need one only when an argument is over a limit (for example, a payment above 100).

Write (plain dicts and lists):

1. `tool_risk(name, table)`: the risk of a tool from `table` (`{name: "low" | "medium" | "high"}`). A tool that is **not** in the table is `"high"`.
2. `needs_approval(name, args, table, limits=None)`: `True` for `"high"`. `False` for `"low"`. For `"medium"`: look up `limits.get(name, {})`, a dict like `{"amount": 100}`. If any `args.get(key, 0)` is **greater than** its limit, return `True`. Otherwise `False` (also when `limits` is `None`).
3. `tools_for_role(role, roles, all_tools)`: `roles` is `{role: [allowed tool names]}`. Return the tools from `all_tools` that the role may use, **in the order of `all_tools`**. An unknown role gets `[]`.

```python
needs_approval("pay", {"amount": 101}, {"pay": "medium"}, {"pay": {"amount": 100}})
# -> True
tools_for_role("reader", {"reader": ["search"]}, ["delete_file", "search"])
# -> ['search']
```

**Think first:** why is "unknown tool means high risk" the right default?

**Hint:** `table.get(name, "high")`. Default to the safe side.
