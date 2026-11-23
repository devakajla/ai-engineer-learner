# Add a NOT NULL column to a table with data

Table `tasks(id, title)` already has rows. Add a required `status` column safely:

**upgrade(op)**
1. add `status` (String(20)) **with `server_default="todo"`** and `nullable=False` — existing rows get `"todo"`
2. create index `ix_tasks_status` on `status`

**downgrade(op)**
1. drop the index
2. drop the column — SQLite needs **batch mode**:

```python
with op.batch_alter_table("tasks") as batch:
    batch.drop_column("status")
```

The tests create the table, insert rows, run your upgrade, check the data, then run downgrade.
