---
title: Databases for backend devs
summary: Why APIs need a database, and the basics (tables, SQL, keys, indexes, transactions, SQL injection) with plain sqlite3 before any ORM.
plan_ids: [SQL-01, SQL-03, SQL-04, SQL-05]
---

TaskFlow keeps its tasks in a Python list. If you restart the server, all tasks are gone. If you run two copies of the server, each copy has its own list.

A **database** fixes both problems. Data **stays** after a restart, and **every copy of the server sees the same data**.

This lesson teaches the database basics that every backend job needs. We use Python's built-in `sqlite3`, so nothing is hidden. In the next lesson you will add the SQLAlchemy ORM on top.

## Why not just a file or a list?

| You need | Python list | Database |
|---|---|---|
| data survives a restart | no | yes |
| many servers share the data | no | yes |
| many writes at once, no damage | no | yes (transactions, locks) |
| fast search on any column | no (read every item) | yes (indexes) |
| combine, count, group data | write it yourself | SQL does it |

This is also why an API should be **stateless**. The state (the data) lives in the database, not inside the web server process.

## Tables, keys and constraints

A relational database stores data in **tables**.

- A **table** has **columns** (each with a type) and **rows** (the records).
- A **primary key** (PK) is a column that identifies each row, like an id number. No two rows have the same one.
- A **foreign key** (FK) is a column that points to the primary key of another table. For example `tasks.owner_id` points to `users.id`. That is how you say "this task belongs to that user".
- **Constraints** are rules the database enforces: `NOT NULL` (a value is required), `UNIQUE` (no duplicates), `CHECK` (a custom rule), and foreign keys.

```sql
CREATE TABLE users (
    id    INTEGER PRIMARY KEY,
    email TEXT NOT NULL UNIQUE
);

CREATE TABLE tasks (
    id       INTEGER PRIMARY KEY,
    title    TEXT NOT NULL,
    priority TEXT NOT NULL DEFAULT 'medium' CHECK (priority IN ('low', 'medium', 'high')),
    done     INTEGER NOT NULL DEFAULT 0,
    owner_id INTEGER REFERENCES users(id) ON DELETE CASCADE
);
```

Notes:

- SQLite has no true boolean, so `done` is `0` (false) or `1` (true).
- `DEFAULT 'medium'` is the value used when you do not give one.
- `ON DELETE CASCADE` means: if the user is deleted, delete their tasks too.

Constraints are your **last line of defence**. Even if your Python code has a bug, the database still refuses bad data.

## SQL in one screen

**SQL** is the language you use to talk to a relational database. The four basic jobs:

```sql
INSERT INTO tasks (title, priority) VALUES ('Write tests', 'high');

SELECT id, title FROM tasks WHERE done = 0 AND priority = 'high' ORDER BY id DESC LIMIT 20 OFFSET 0;

UPDATE tasks SET done = 1 WHERE id = 7;

DELETE FROM tasks WHERE id = 7;
```

- `SELECT ... WHERE` picks rows. `ORDER BY` sorts. `LIMIT` and `OFFSET` give paging.
- **Always** put a `WHERE` on `UPDATE` and `DELETE`. Without it, you change or delete **every** row.

### Counting and grouping

`GROUP BY` puts rows with the same value into one group, so you can count each group:

```sql
SELECT priority, COUNT(*) AS n FROM tasks GROUP BY priority;
```

`HAVING` filters the **groups** (like `WHERE`, but after counting):

```sql
SELECT priority, COUNT(*) AS n FROM tasks GROUP BY priority HAVING COUNT(*) > 1;
```

### Joining two tables

A **join** combines rows from two tables, using the key that links them.

- `INNER JOIN` keeps only the rows that have a match in both tables.
- `LEFT JOIN` keeps **every** row from the left table. When there is no match, the right-side values are `NULL`.

Example: how many open tasks does each user have, including users who have none?

```sql
SELECT u.email, COUNT(t.id) AS open_tasks
FROM users u
LEFT JOIN tasks t ON t.owner_id = u.id AND t.done = 0
GROUP BY u.id
ORDER BY open_tasks DESC;
```

Read it slowly:

1. Start with every user (`FROM users u`).
2. Attach their open tasks (`LEFT JOIN tasks t ON ...`). A user with none still stays, with `t.id` = `NULL`.
3. Group by user and count `t.id`. `COUNT(t.id)` does not count `NULL`, so a user with no tasks gets `0`.

Here is a full run on a different problem: authors and books.

```python
import sqlite3

conn = sqlite3.connect(":memory:")
conn.executescript("""
    CREATE TABLE authors (id INTEGER PRIMARY KEY, name TEXT);
    CREATE TABLE books (id INTEGER PRIMARY KEY, title TEXT, author_id INTEGER);
    INSERT INTO authors VALUES (1, 'Ana'), (2, 'Ben');
    INSERT INTO books VALUES (1, 'Sea', 1), (2, 'Sky', 1);
""")

rows = conn.execute("""
    SELECT a.name, COUNT(b.id) AS n
    FROM authors a
    LEFT JOIN books b ON b.author_id = a.id
    GROUP BY a.id
    ORDER BY n DESC, a.name
""").fetchall()
print(rows)   # -> [('Ana', 2), ('Ben', 0)]
```

Ben has no books, but he still appears, with `0`. With an `INNER JOIN` he would be missing.

## Using SQL from Python: `sqlite3`

Python has a database tool built in, called `sqlite3`.

```python
import sqlite3

conn = sqlite3.connect("taskflow.db")       # a file; created if missing
conn.row_factory = sqlite3.Row              # rows can be turned into dicts

conn.execute("CREATE TABLE IF NOT EXISTS tasks (id INTEGER PRIMARY KEY, title TEXT NOT NULL, done INTEGER NOT NULL DEFAULT 0)")

cur = conn.execute("INSERT INTO tasks (title) VALUES (?)", ("Write tests",))
conn.commit()                               # save the change
new_id = cur.lastrowid                      # the id the database gave

row = conn.execute("SELECT * FROM tasks WHERE id = ?", (new_id,)).fetchone()
print(dict(row))    # -> {'id': 1, 'title': 'Write tests', 'done': 0}
conn.close()
```

Things to know:

- `conn.execute(sql, values)` runs one statement. The values go in a tuple. A tuple with one value needs a trailing comma: `("Write tests",)`.
- `.fetchone()` gives one row, or `None` if there is none. `.fetchall()` gives a list of all rows.
- Changes are **not saved until `conn.commit()`**. If you forget it, they disappear when the connection closes.
- `":memory:"` instead of a file name gives a temporary database that lives only in memory. It is perfect for tests.

## SQL injection: always use `?`

**SQL injection** is one of the most famous attacks. A user types SQL code into a form, and your program runs it.

```python
title = "x'); DROP TABLE tasks; --"

conn.execute(f"INSERT INTO tasks (title) VALUES ('{title}')")      # NEVER: the user writes your SQL
conn.execute("INSERT INTO tasks (title) VALUES (?)", (title,))      # SAFE
```

In the first line, the text is pasted into the SQL, and the attacker's `DROP TABLE` runs. In the second line, you use a **placeholder** `?`. The database gets the SQL and the values **separately**, so the value can never become part of the command.

The rule: **never build SQL with f-strings or `+` using user input. Always use placeholders.** (`?` in sqlite3. Other databases use `%s` or `:name`.)

For a search with `LIKE`, build the pattern in Python, then pass it as a value:

```python
text = "sql"
pattern = f"%{text}%"       # % means "anything"
rows = conn.execute("SELECT * FROM tasks WHERE title LIKE ?", (pattern,)).fetchall()
```

`LIKE` in SQLite ignores upper and lower case for normal letters.

## Worked example: a small repository with sqlite3

Exercise 1 asks you to write functions that create a table, add a row, get a row, and search. Here is the same pattern for a different problem: **contacts**.

Goal:

```python
conn = sqlite3.connect(":memory:")
create_schema(conn)
cid = add_contact(conn, "Ana", "111")
get_contact(conn, cid)       # -> {"id": 1, "name": "Ana", "phone": "111"}
find(conn, "an")             # -> [{"id": 1, "name": "Ana", "phone": "111"}]
```

**Step 1.** Create the table.

```python
def create_schema(conn):
    conn.execute("CREATE TABLE contacts (id INTEGER PRIMARY KEY, name TEXT NOT NULL, phone TEXT NOT NULL DEFAULT '')")
```

**Step 2.** Insert with `?`, commit, and return the new id.

```python
def add_contact(conn, name, phone=""):
    cur = conn.execute("INSERT INTO contacts (name, phone) VALUES (?, ?)", (name, phone))
    conn.commit()
    return cur.lastrowid
```

**Step 3.** Fetch one row. Turn it into a dict, or return `None` if it is missing.

```python
def get_contact(conn, contact_id):
    row = conn.execute("SELECT id, name, phone FROM contacts WHERE id = ?", (contact_id,)).fetchone()
    if row is None:
        return None
    return {"id": row[0], "name": row[1], "phone": row[2]}
```

A row is a tuple, so `row[0]` is the first column.

**Step 4.** Search with a `LIKE` pattern, as a parameter.

```python
def find(conn, text):
    rows = conn.execute(
        "SELECT id, name, phone FROM contacts WHERE name LIKE ? ORDER BY id", (f"%{text}%",)
    ).fetchall()
    return [{"id": r[0], "name": r[1], "phone": r[2]} for r in rows]
```

**Step 5.** Run the goal and check it.

```python
conn = sqlite3.connect(":memory:")
create_schema(conn)
cid = add_contact(conn, "Ana", "111")
print(get_contact(conn, cid))    # -> {'id': 1, 'name': 'Ana', 'phone': '111'}
print(find(conn, "an"))          # -> [{'id': 1, 'name': 'Ana', 'phone': '111'}]
print(get_contact(conn, 99))     # -> None
```

## Indexes

Without help, `WHERE done = 0` must read **every row** of the table (a *full table scan*). With a million rows, that is slow.

An **index** is a sorted list kept by the database, like the index at the back of a book. With it, the database finds matching rows quickly, without reading the whole table.

```sql
CREATE INDEX ix_tasks_done ON tasks (done);
CREATE INDEX ix_tasks_owner_done ON tasks (owner_id, done);   -- two columns: the order matters
```

The price: an index makes **reads faster but writes slower** (each insert has to update it), and it uses disk space. So index the columns you often **filter, join or sort on**. Primary keys and `UNIQUE` columns are indexed automatically.

To see whether the database uses an index: `EXPLAIN QUERY PLAN SELECT * FROM tasks WHERE done = 0;`.

## Transactions and ACID

A **transaction** is a group of statements that succeed or fail **together**.

The classic example is moving money:

```python
try:
    conn.execute("UPDATE accounts SET balance = balance - 100 WHERE id = ?", (1,))
    conn.execute("UPDATE accounts SET balance = balance + 100 WHERE id = ?", (2,))
    conn.commit()        # both happened
except Exception:
    conn.rollback()      # undo everything: neither happened
    raise
```

If the second update fails, the first one must not stay. Otherwise 100 rupees vanish.

Python makes this shorter. A `with conn:` block **commits** if the code inside works, and **rolls back** if it raises an error:

```python
with conn:
    conn.execute("UPDATE accounts SET balance = balance - 100 WHERE id = ?", (1,))
    conn.execute("UPDATE accounts SET balance = balance + 100 WHERE id = ?", (2,))
```

(The `with` statement is a context manager, from Python lesson 24. It does not close the connection, only the transaction.)

Two more useful details:

- After an `UPDATE`, `cursor.rowcount` tells you **how many rows changed**. If it is `0`, no row matched, for example because the id does not exist.
- If a `CHECK` rule fails (like `balance >= 0`), the database raises `sqlite3.IntegrityError`. Inside `with conn:`, that error also triggers the rollback.

Transactions follow four promises, called **ACID**:

| Letter | Name | Meaning |
|---|---|---|
| A | Atomicity | all statements succeed, or none do |
| C | Consistency | the rules (constraints) hold before and after |
| I | Isolation | transactions running at the same time do not see each other's half-finished work |
| D | Durability | once committed, the data survives a crash |

## SQLite vs PostgreSQL

- **SQLite** is a single file with no separate server. It is perfect for learning, tests and small apps. But it allows only **one writer at a time**.
- **PostgreSQL** is a real database server made for many users at once. It has rich types (JSON, arrays) and extensions such as **pgvector**, used for AI embeddings. It is the usual choice for production.

When you use an ORM (next lesson), switching between them is mostly a change of one address. That is why TaskFlow starts on SQLite.

## Backend concept: connections in a web app

- Opening a connection is slow. Production apps keep a **connection pool**: a set of ready connections to reuse. SQLAlchemy does this for you.
- Use **one connection (or session) per request**, and release it at the end. This is the `yield` dependency pattern from lesson 8.
- In this lesson's project step, our simple SQLite repository opens a **short-lived connection for each operation**. That is simple and safe.

## A little deeper (optional)

- `executescript(...)` runs several SQL statements at once. It is handy for set-up in tests.
- A **composite index** on `(owner_id, done)` helps queries that filter by `owner_id`, or by both. It does not help a query that filters only by `done`. This is why "the order matters".
- When you must build a column name dynamically (for example in an `UPDATE`), you cannot use `?` for the name. Only allow names from a fixed list that you wrote yourself.

## Common mistakes

- Building SQL with f-strings. That is SQL injection.
- Forgetting `commit()`. The change is lost when the connection closes.
- Forgetting `WHERE` in `UPDATE` or `DELETE`.
- No index on columns you filter by. The API gets slow as data grows.
- Trusting only your Python code and writing no constraints.
- Saving booleans and dates in different formats. In SQLite, choose one: `0`/`1` for booleans, ISO text for dates.

## Interview corner

- **Q: How do you prevent SQL injection?** Use parameterized queries (placeholders) or an ORM. Never put user input into the SQL text.
- **Q: What is an index, and what does it cost?** A sorted structure (usually a B-tree) that makes lookups fast. It costs write speed and disk space.
- **Q: Explain ACID.** Atomicity, Consistency, Isolation, Durability, as in the table above.
- **Q: INNER JOIN vs LEFT JOIN?** Inner keeps only the rows with a match. Left keeps every row of the left table, with `NULL` where nothing matches.
- **Q: Why should web servers be stateless?** Then any copy of the server can answer any request, and you can add more copies to scale. State goes in the database or a cache.

## Summary

- A database gives you persistence, sharing, safe concurrent writes and fast queries.
- Tables, primary keys, foreign keys and constraints. SQL for CRUD, `GROUP BY` and joins.
- **Always** use parameterized queries (`?`).
- Index the columns you filter, join or sort on. Indexes cost write speed.
- A transaction is all-or-nothing (ACID). Use `with conn:` to commit or roll back.
