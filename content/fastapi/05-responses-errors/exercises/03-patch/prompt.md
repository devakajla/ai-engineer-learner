# PATCH done right

`PROFILE` holds one profile. Create a `ProfileUpdate` model where **every field is optional** (`name`: str 1–50, `bio`: str or None, `city`: str or None) and a route `PATCH /profile` that:

- updates **only the fields the client sent**
- returns the full updated profile

```text
PROFILE = {"name": "Dev", "bio": "Backend dev", "city": "Pune"}

PATCH /profile {"city": "Bengaluru"}  -> {"name": "Dev", "bio": "Backend dev", "city": "Bengaluru"}
PATCH /profile {"bio": null}          -> {"name": "Dev", "bio": null, "city": "Bengaluru"}
PATCH /profile {}                     -> unchanged
PATCH /profile {"name": ""}           -> 422
```

Hint: `model_dump(exclude_unset=True)`.
