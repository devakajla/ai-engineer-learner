# May this user see this chunk?

Write `allowed(chunk, user)`. It decides if a user may see a chunk.

- A chunk has `"tenant"` (the customer or company it belongs to) and, optionally, `"groups"` (a list of group names that may read it).
- A user has `"tenant"` and, optionally, `"groups"` (a list).

Rules:
1. Different tenants: `False`. Always. This rule comes first.
2. The same tenant, and the chunk has **no groups** (missing or empty): `True` (everyone in the tenant may read it).
3. The chunk has groups: `True` only if the user has **at least one** of them.

```python
chunk = {"tenant": "acme", "groups": ["hr"]}
allowed(chunk, {"tenant": "acme", "groups": ["hr", "dev"]})   # -> True
allowed(chunk, {"tenant": "acme", "groups": ["dev"]})         # -> False
allowed({"tenant": "acme"}, {"tenant": "acme"})               # -> True
allowed({"tenant": "acme"}, {"tenant": "other"})              # -> False
```
