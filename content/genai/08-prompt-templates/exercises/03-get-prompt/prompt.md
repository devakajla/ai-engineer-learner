# Get a prompt by name and version

Prompts are stored like this: `{"qa": {"v1": "...", "v2": "..."}, ...}`.

Write `get_prompt(registry, name, version=None)`.

Rules:
- If `version` is given, return that version's text.
- If `version` is `None`, return the text of the **latest** version. The latest version has the biggest number after the `v` (`"v10"` is later than `"v2"`).
- If the name is not in `registry`, raise `KeyError(name)`.
- If the version is not found, raise `KeyError(version)`.
- Version names look like `"v1"`, `"v2"`, `"v10"`.

```python
registry = {"qa": {"v1": "A", "v2": "B", "v10": "C"}}

get_prompt(registry, "qa", "v1")   # -> 'A'
get_prompt(registry, "qa")         # -> 'C'
get_prompt(registry, "zzz")        # raises KeyError
```
