---
title: Migrations with Alembic
summary: Change a live database safely and repeatably with revisions, autogenerate, upgrade, downgrade and data migrations.
plan_ids: [SQL-08]
---

Your database design will change again and again: a new column, a new table, a new index. In the last lesson you used `Base.metadata.create_all()`. It only creates **missing tables**. It never changes a table that already exists, and it keeps no history.

In real projects you use **migrations**. A migration is a small, versioned script that changes the database structure. Everyone's database (yours, your teammate's, the test server, production) goes through the **same changes in the same order**.

For SQLAlchemy, the migration tool is **Alembic**.

## The mental model

Think of migrations like a chain of save points in a game:

```
0001_create_tasks  ->  0002_add_due_date  ->  0003_add_users  ->  (head)
```

- Each **revision** is a Python file with two functions: `upgrade()` (go forward) and `downgrade()` (go back).
- Each revision has an id (`revision`) and points to the one before it (`down_revision`). That makes the chain.
- The database remembers where it is, in a small table called **`alembic_version`**.
- **`head`** means the newest revision.
- `alembic upgrade head` applies every revision the database has not seen yet. `alembic downgrade -1` undoes the last one.

Migrations are **code**. They are reviewed like other code, and they are run by the deploy pipeline. Nobody runs them by hand on the production database.

## Setup

```bash
uv add alembic
uv run alembic init migrations
```

This creates `alembic.ini` and a folder `migrations/` with `env.py` and `versions/`.

Open `migrations/env.py` and point Alembic at your models and at your settings:

```python
from app.core.config import get_settings
from app.db.base import Base
import app.db.models  # noqa: F401  (this import registers the models on Base.metadata)

config.set_main_option("sqlalchemy.url", get_settings().database_url)
target_metadata = Base.metadata
```

Now the database address comes from the same settings as your app (from environment variables). It is not typed into `alembic.ini`.

## Writing a revision

```bash
uv run alembic revision -m "add due_date to tasks"
```

This creates a new file in `migrations/versions/`. Fill in the two functions:

```python
import sqlalchemy as sa
from alembic import op

revision = "0002"
down_revision = "0001"

def upgrade() -> None:
    op.add_column("tasks", sa.Column("due_date", sa.DateTime(timezone=True), nullable=True))

def downgrade() -> None:
    op.drop_column("tasks", "due_date")
```

- `upgrade` does the change. `downgrade` does the **exact opposite**.
- `op` has the actions: `op.create_table`, `op.drop_table`, `op.add_column`, `op.drop_column`, `op.alter_column`, `op.create_index`, `op.drop_index`, `op.create_foreign_key`, and `op.execute(sql)` for running SQL.
- `sa.Column(...)` describes a column with its type and rules, like `nullable=False` or `unique=True`.

## Worked example: a migration that creates a table

Exercise 1 asks for a migration that creates a table and an index, and a downgrade that removes them. Here is the same pattern for a different problem: a table called **`tags`**.

Goal for `upgrade`: table `tags` with `id` (primary key), `label` (text up to 50, required, unique), `hidden` (true/false, required, default false), and an index on `hidden`.

In the exercise, `op` is **passed in** as a parameter, so tests can run your code on a temporary database. In a real project you import it from `alembic`. The code inside is the same.

**Step 1.** Write `upgrade` with `op.create_table`. Each column is a `sa.Column(...)`.

```python
import sqlalchemy as sa

def upgrade(op):
    op.create_table(
        "tags",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("label", sa.String(50), nullable=False, unique=True),
        sa.Column("hidden", sa.Boolean(), nullable=False, server_default=sa.false()),
    )
```

`server_default` is a default that the **database** applies. `sa.false()` is the database-safe `false`.

**Step 2.** Add the index in the same function.

```python
    op.create_index("ix_tags_hidden", "tags", ["hidden"])
```

The arguments are: the index name, the table name, and a **list** of columns.

**Step 3.** Write `downgrade`. Do the steps in **reverse order**: drop the index first, then the table.

```python
def downgrade(op):
    op.drop_index("ix_tags_hidden", table_name="tags")
    op.drop_table("tags")
```

**Step 4.** Try both on a temporary in-memory database. This is how the tests will work, too.

```python
from alembic.migration import MigrationContext
from alembic.operations import Operations

engine = sa.create_engine("sqlite://")
with engine.begin() as conn:
    op = Operations(MigrationContext.configure(conn))

    upgrade(op)
    print(sa.inspect(conn).get_table_names())    # -> ['tags']

    downgrade(op)
    print(sa.inspect(conn).get_table_names())    # -> []
```

A good migration can go up and down without leaving anything behind.

## Autogenerate

Writing every change by hand is slow. Alembic can **draft** a migration for you:

```bash
uv run alembic revision --autogenerate -m "add due_date"
```

It compares your models (`Base.metadata`) with the real database and writes the differences.

But **always read and edit the result**. It is only a draft:

- It cannot see **renames**. If you rename a column, it sees "one column removed, one added". Running that would **delete the data**.
- Some changes (server defaults, some type changes) need your attention.

## Running migrations

```bash
uv run alembic upgrade head      # go to the newest revision
uv run alembic downgrade -1      # go back one step
uv run alembic current           # which revision is this database at?
uv run alembic history           # show the whole chain
```

In a deploy, the order is: **run the migration first, then start the new version of the app**.

## SQLite needs batch mode

SQLite cannot change most things on an existing table (like dropping a column). Alembic has **batch mode**: it makes a new table, copies the data, and swaps them.

```python
with op.batch_alter_table("tasks") as batch:
    batch.drop_column("legacy_flag")
```

Set `render_as_batch=True` in `env.py`, so autogenerate writes batch code for SQLite.

## Adding a required column to a table with data

Say `tasks` already has 1,000 rows and you want a new required column `status`. If you add a `NOT NULL` column with no default, the old rows have nothing to put there, and the migration fails.

The safe way is to give the column a **`server_default`**. Then old rows get the default value:

```python
def upgrade(op):
    op.add_column(
        "tasks",
        sa.Column("status", sa.String(20), nullable=False, server_default="todo"),
    )

def downgrade(op):
    with op.batch_alter_table("tasks") as batch:
        batch.drop_column("status")
```

Result on a table that has a row `(1, 'x')`: after the upgrade the row is `(1, 'x', 'todo')`. After the downgrade it is `(1, 'x')` again.

## Data migrations

Sometimes the **data** must change, not only the structure. For example, you split `nick` into two columns. The steps:

1. Add the new column (empty is allowed).
2. Read the old rows and fill the new column.
3. Only then drop the old column, if you want.

```python
def upgrade(op):
    op.add_column("people", sa.Column("shout", sa.String(100), nullable=True))

    conn = op.get_bind()                                   # the live database connection
    rows = conn.execute(sa.text("SELECT id, nick FROM people")).fetchall()
    for row in rows:
        conn.execute(
            sa.text("UPDATE people SET shout = :s WHERE id = :id"),
            {"s": row.nick.upper(), "id": row.id},
        )
```

- `op.get_bind()` gives a connection. `sa.text("...")` is a piece of raw SQL.
- Values go in with **named placeholders** (`:s`, `:id`) and a dictionary. That keeps it safe from SQL injection, just like `?` in lesson 9.
- **Do not import your app's models inside a migration.** Models change over time, but a migration from last year must still work the same. Use `sa.text(...)` or `sa.table(...)`.

## Backend concept: safe changes while the app is running

During a deploy, the **old** and the **new** version of the app often run **at the same time** for a short while. A migration must not break the old version. Some safe habits:

- **New required column:** add it as nullable or with a default, fill the old rows, and make it strict later.
- **Rename a column:** do not rename it in one step. Add the new column, write to both, copy the old data, switch reads to the new column, and drop the old one in a later release. (Think: *expand*, then *migrate*, then *contract*.)
- **Remove a column:** first deploy code that no longer uses it. Drop it in a later release.
- **Big tables:** create indexes without locking the table (in Postgres, `CREATE INDEX CONCURRENTLY`), and copy data in small batches.

## A little deeper (optional)

- `down_revision = None` marks the very first revision.
- An Alembic revision file runs in order of the chain, not in order of file names. The name prefix like `0002_` only helps humans.
- If you use Alembic, do not keep `create_all` in your startup code. Two ways of creating tables means two sources of truth, and they will disagree.

## Common mistakes

- Editing a migration that has already run somewhere. Make a **new** migration instead.
- Trusting autogenerate without reading it (a rename becomes drop and add, and the data is lost).
- Typing the database address in `alembic.ini`.
- Adding a `NOT NULL` column without a default to a table that has rows.
- Importing app models inside a migration.

## Interview corner

- **Q: Why migrations instead of `create_all`?** Migrations are versioned, reviewable and repeatable. `create_all` cannot change existing tables and keeps no history.
- **Q: How do you rename a column with zero downtime?** Expand and contract: add the new column, write to both, copy the old data, move reads to the new column, then drop the old column in a later release.
- **Q: What does the `alembic_version` table store?** The id of the revision that database is currently at.
- **Q: What can autogenerate not detect?** Renames (seen as drop and add), some default and type changes, and data changes.

## Summary

- A revision has `upgrade` and `downgrade`. Revisions form a chain with `down_revision`. The database stores its position in `alembic_version`.
- `env.py` reads the address from your settings and sets `target_metadata = Base.metadata`.
- `revision --autogenerate` makes a draft. You must review it.
- `upgrade head` and `downgrade -1`. Migrate **before** starting the new app version.
- SQLite needs batch mode. Plan risky changes in steps (expand, then contract).
