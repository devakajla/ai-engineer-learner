# Simplify a path

`path` is an absolute Unix path (starts with `/`). Write `simplify_path(path)` that returns the **shortest** form: `.` means "this folder" (ignore), `..` means "go up one" (at the root it stays at the root), several `/` count as one, and there is no `/` at the end (except for the root `/`).

```python
simplify_path("/home//foo/")            # -> "/home/foo"
simplify_path("/a/./b/../../c/")        # -> "/c"
```

**Think first:** which folder does `..` remove: the first one or the latest one you entered?

**Hint:** pattern *stack*: `for part in path.split("/")`: skip `""` and `"."`; on `".."` pop if the stack is not empty; else push. Result `"/" + "/".join(stack)`.
