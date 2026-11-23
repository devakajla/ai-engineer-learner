# Clean and check a signup

Create `app` with `POST /signup`. The body model `SignupIn` has two text fields, `username` and `password`. Write the rules with `field_validator`:

- `username`: remove spaces at both ends, then make it lowercase. After that it must be **3 to 20 characters** and contain only letters, digits and `_`.
- `password`: at least **8 characters**, with **at least one letter and one digit**.

When the data is valid, answer **201** with only the cleaned username: `{"username": "<clean username>"}`. Never send the password back.

```text
POST /signup {"username": "  Dev_99 ", "password": "secret123"}  -> 201 {"username": "dev_99"}
POST /signup {"username": "a!", "password": "secret123"}         -> 422
POST /signup {"username": "devdev", "password": "onlyletters"}   -> 422
```

**Think first:** Should you clean the text first and check it after, or the other way around?

**Hint:** `@field_validator("username")` on a `@classmethod`. Return the cleaned value. Raise `ValueError("...")` for a bad value. Text methods: `strip()`, `lower()`, `isalnum()`, `any(...)`.
