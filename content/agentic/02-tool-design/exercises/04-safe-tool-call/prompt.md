# One safe door for every tool call

Now put the pieces together. Every tool call from the model should pass through **one** function that never crashes and always returns text the model can learn from.

In the starter you get `validate_args` and `truncate_result` from the earlier exercises. Write `safe_tool_call(tools, functions, name, args, max_chars=500)`:

- `tools`: the list of tool dictionaries (as in exercise 1).
- `functions`: a dictionary `{name: python function}`.
- `name`, `args`: what the model asked for (`args` is already a dictionary).

It returns **a string** for the tool message, decided in this order:

1. The tool is not in `tools`, or the name is not in `functions`: `"error: unknown tool <name>. Available tools: <names>"`. `<names>` are the tool names from `tools`, **sorted** and joined with `", "`. If `tools` is empty, write `(none)`.
2. `validate_args(tool, args)` gives problems: `"error: "` followed by the problems joined with `"; "`. The function is **not** called.
3. The function raises an exception `e`: `"error: <ExceptionClassName>: <message>"`, for example `error: ZeroDivisionError: division by zero`.
4. Otherwise `truncate_result(str(result), max_chars)`.

```python
safe_tool_call(tools, {"add": add}, "add", {"a": 1, "b": 2})        # -> '3'
safe_tool_call(tools, {"add": add}, "sub", {})                       # -> 'error: unknown tool sub. Available tools: add'
safe_tool_call(tools, {"div": div}, "div", {"a": 1, "b": 0})         # -> 'error: ZeroDivisionError: division by zero'
```

**Think first:** why do the error texts say what is wrong **and** what is available or expected? What will the model do with them on its next step?

**Hint:** `type(error).__name__` is the class name of an exception. A `try` / `except Exception as error` catches it.
