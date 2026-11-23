# Read a pyproject.toml

Write `read_project(text)`. `text` is the content of a `pyproject.toml`. Return a dict:

```python
{"name": str, "version": str, "requires_python": str, "dependencies": [names], "dev_dependencies": [names]}
```

Rules:

- `dependencies` and `dev_dependencies` hold only the **library names**, with the version rules removed, in the original order. Dev ones come from `[dependency-groups]` `dev`.
- Missing optional parts get defaults: `version` is `"0.0.0"`, `requires_python` is `""`, the lists are `[]`.
- No `[project]` section, or no `name` in it: raise `ValueError`.
- Text that is not valid TOML: raise `ValueError` too.

```python
read_project('[project]\nname = "app"\nversion = "1.2.0"\ndependencies = ["fastapi>=0.110", "httpx"]\n')
# -> {"name": "app", "version": "1.2.0", "requires_python": "", "dependencies": ["fastapi", "httpx"], "dev_dependencies": []}
```

**Think first:** What does `tomllib.loads` raise for bad text? How do you split `"fastapi>=0.110"` into a name and a rule?

**Hint:** Use `tomllib.loads`, `.get(...)` with defaults, and `re.split(r"[<>=!~;\[ ]", requirement)[0]` (or a similar way) to get the name.
