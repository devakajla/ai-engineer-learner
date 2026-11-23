# Access rule

A user may open a document if they are an **admin or the owner**, and they are **not banned**. Write `can_access(is_admin, is_owner, is_banned)` returning a `bool`.

```python
can_access(True, False, False)   # -> True
can_access(False, True, False)   # -> True
can_access(False, False, False)  # -> False
can_access(True, True, True)     # -> False   banned beats everything
```

Watch the precedence of `and` vs `or`.
