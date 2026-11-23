# Mask an email

For logs we must hide most of an email address. Write `mask_email(email)` that keeps the **first character** of the part before `@`, replaces the rest of that part with `*`, and keeps the domain as-is.

```python
mask_email("dev@example.com")       # -> "d**@example.com"
mask_email("kunal.k@gmail.com")     # -> "k******@gmail.com"
mask_email("a@b.io")                # -> "a@b.io"
```

You may assume exactly one `@` and a non-empty part before it. Hint: `"ab" * 3` → `"ababab"`, and look at `partition`.
