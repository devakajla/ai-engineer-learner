# Did the agent take the right path?

To test an agent, you can compare the tools it **actually called** with the tools it **should have called**. This is called **trajectory evaluation**. It is cheap and does not need a model judge.

Write `check_tool_path(expected, actual)`. Both are lists of tool names. Return a dictionary with three keys:

- `"all_called"`: `True` if every name in `expected` appears in `actual`.
- `"in_order"`: `True` if the names of `expected` appear in `actual` **in the same order**. Other calls may sit between them. (This is called a *subsequence*.) For example `["a", "c"]` is in order in `["a", "b", "c"]`, but `["c", "a"]` is not.
- `"extra"`: the names in `actual` that are **not** in `expected`, each listed once, in the order they first appeared.

An empty `expected` gives `all_called` and `in_order` as `True`.

```python
check_tool_path(["search", "summarize"], ["search", "fetch", "summarize"])
# -> {'all_called': True, 'in_order': True, 'extra': ['fetch']}
check_tool_path(["search", "summarize"], ["summarize", "search"])
# -> {'all_called': True, 'in_order': False, 'extra': []}
```

**Think first:** an agent reaches the right answer but with 3 extra tool calls. Is that a pass or a fail? What does "extra" tell you about cost?

**Hint:** walk through `actual` with a pointer into `expected`. Move the pointer when the current name matches the next expected one. At the end, check whether the pointer reached the end.
