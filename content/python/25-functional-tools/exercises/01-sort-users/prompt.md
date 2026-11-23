# Sorting and searching with keys

`users` is a list of dicts like `{"name": "ana", "age": 31, "active": True}`.

Write:

- `by_age_desc_name(users)` → new list sorted by age **descending**, then name **ascending, case-insensitive**
- `oldest_active(users)` → the oldest user with `active == True`, or `None` if there is none (use `max` with `key` and `default`)
- `has_minor(users)` → `True` if any user is under 18 (use `any`)
- `names_by_id(ids, names)` → a dict mapping id → name; raise `ValueError` if the two lists have different lengths (hint: `zip(..., strict=True)`)

The input list must not be modified.
