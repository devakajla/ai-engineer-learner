# A data migration

Table `users(id, full_name)` stores names like `"Ada Lovelace"`. The team wants `first_name` and `last_name` instead.

**upgrade(op)**
1. add `first_name` and `last_name` (String(100), nullable)
2. **backfill** them from `full_name` — first word → `first_name`, the rest → `last_name` (`""` if there is only one word). Read rows with `op.get_bind().execute(sa.text(...))` and update with **parameterized** `sa.text("UPDATE ... WHERE id = :id")`.
3. drop `full_name` (batch mode)

**downgrade(op)**: the reverse — add `full_name`, fill it with `first_name || ' ' || last_name` trimmed, drop the two columns.

Do **not** import any ORM models — migrations must be self-contained.
