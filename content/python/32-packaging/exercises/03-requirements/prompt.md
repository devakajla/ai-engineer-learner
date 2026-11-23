# Tidy a requirements list

Write two functions:

- `split_requirement(text)` → `(name, rule)`. `name` is the library name **lowercased, with `_` replaced by `-`**. `rule` is the rest with all spaces removed (`""` if there is none). The name is the first run of letters, digits, `-`, `_` and `.`. Raise `ValueError` if there is no name.
- `merge_requirements(existing, new)` → a new list of requirement texts. Both inputs are lists of texts. If a name appears in both (compare the normalised names), the **new** one wins. The result has **one entry per name**, sorted by normalised name. Each entry is written as `name + rule` (normalised name, then the rule). The input lists must not be changed.

```python
split_requirement("Typing_Extensions >= 4.0, < 5")   # -> ("typing-extensions", ">=4.0,<5")
merge_requirements(["httpx>=0.20", "fastapi"], ["HTTPX>=0.27", "pytest"])
# -> ["fastapi", "httpx>=0.27", "pytest"]
```

**Think first:** Why must `Typing_Extensions` and `typing-extensions` be treated as the same library? What data structure helps keep only one entry per name?

**Hint:** Use `re.match` for the name. Put the entries in a dict keyed by name: first the existing ones, then the new ones, so new ones replace old ones. Then sort.
