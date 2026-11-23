# A service that is easy to test

Write a class `SignupService` that gets two helpers when it is created: a `store` and a `mailer`.

- `SignupService(store, mailer)`
- `signup(email)`:
  - the email is cleaned first: spaces removed from both ends and lowercased
  - an email without exactly one `@` raises `ValueError("invalid email")`
  - if `store.exists(email)` is true, raise `ValueError("already registered")`
  - otherwise call `store.add(email)`, then `mailer.send(email, "Welcome!")`, and return the cleaned email
- If anything fails, **nothing** may be added to the store and **no** email may be sent.

The tests pass in their own fake `store` (with `exists` and `add`) and fake `mailer` (with `send`).

```python
service = SignupService(store, mailer)
service.signup("  Ana@X.io ")      # -> "ana@x.io"   (store.add and mailer.send were called once)
service.signup("nope")             # raises ValueError("invalid email")
```

**Think first:** Where should the checks go, before or after the store is changed? What does the service need from its helpers?

**Hint:** Keep the helpers on `self`, validate first, and only then call `add` and `send`.
