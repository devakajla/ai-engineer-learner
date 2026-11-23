# Your first migration

In a real project `op` is imported from `alembic`. Here it's **passed in** so the tests can run your migration against a temporary database.

Write `upgrade(op)` and `downgrade(op)`:

**upgrade** creates table `projects`:

| column | type | rules |
|---|---|---|
| `id` | Integer | primary key |
| `name` | String(100) | not null, **unique** |
| `archived` | Boolean | not null, `server_default=sa.false()` |
| `created_at` | DateTime(timezone=True) | not null, `server_default=sa.func.now()` |

…and an index `ix_projects_archived` on `archived`.

**downgrade** drops the index and the table (reverse order of upgrade).

```python
def upgrade(op):
    op.create_table("projects", sa.Column("id", sa.Integer(), primary_key=True), ...)
```
