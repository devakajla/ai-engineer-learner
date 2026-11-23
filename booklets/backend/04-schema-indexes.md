# 4. Schema design, indexes and the N+1 problem

A **schema** is the plan of your tables: which tables, which columns, how they link. A bad schema hurts for years, because changing it later means moving real data. A good schema makes queries simple and fast.

This chapter also covers **indexes** (how a database finds rows fast) and the **N+1 problem** (the most common reason an API is slow).

## Relationships between tables

There are three kinds.

@@ grid 3 | Figure 4.1: the three relationship types.
One to one|one user has one profile;profile.user_id (unique)|blue
One to many|one user has many orders;orders.user_id points to users.id|green
Many to many|students and courses;needs a middle table|yellow
@@ end

**One to many** is the most common. The "many" side holds the foreign key (`orders.user_id`).

**Many to many** needs a **join table** (also called a link table):

| students | | enrollments | | courses |
| --- | --- | --- | --- | --- |
| id, name | ← | student_id, course_id | → | id, title |

```sql
CREATE TABLE enrollments (
  student_id INT REFERENCES students(id),
  course_id  INT REFERENCES courses(id),
  PRIMARY KEY (student_id, course_id)   -- the same pair cannot repeat
);
```

## Normalization: do not repeat yourself

**Normalization** means each fact is stored in exactly one place.

Bad design. The city of a user is copied into every order:

| order_id | user_name | user_city | item |
| --- | --- | --- | --- |
| 10 | Asha | Pune | Laptop |
| 11 | Asha | Pune | Mouse |

If Asha moves to Goa, you must update every order. Miss one and the data disagrees with itself.

Good design: `users` holds the city once, `orders` holds only `user_id`.

The three rules in plain words:

| Form | Rule | Plain words |
| --- | --- | --- |
| 1NF | each cell holds one value | no "Laptop, Mouse" in one cell |
| 2NF | each column depends on the *whole* key | matters for keys of two columns |
| 3NF | columns depend on the key, not on other columns | `city` belongs to the user, not to the order |

> Short memory aid: *every column describes the key, the whole key, and nothing but the key.*

### When to denormalize

**Denormalizing** means copying data on purpose, for speed. Example: storing `order_count` on the user so you do not count every time. It makes reads fast and writes harder, because you must keep copies in sync. Do it only when you measured a real problem.

### Good habits for tables

- Every table gets a primary key.
- Use the right type: `INT`, `TEXT`, `NUMERIC` for money (never `FLOAT`), `TIMESTAMPTZ` for time.
- Add `created_at` and `updated_at`.
- Add `NOT NULL`, `UNIQUE` and foreign keys. Let the database enforce the rules, not only your code.
- **Soft delete**: instead of deleting a row, set `deleted_at`. You can undo it later.

## Indexes

Imagine a 500 page book. To find "photosynthesis", you do not read every page. You open the **index** at the back. A database index is the same idea.

Without an index, Postgres reads **every row** to find a match. This is a **sequential scan**. With 10 rows it is fine. With 10 million rows it takes seconds.

```sql
CREATE INDEX idx_orders_user_id ON orders (user_id);
```

Now `WHERE user_id = 7` jumps straight to the right rows.

@@ flow | Figure 4.2: finding user_id = 7.
Without index|read all 10,000,000 rows|red -> With index|walk a small tree;read a few pages|green
@@ end

The default index is a **B-tree**. It keeps values sorted, so it is fast for `=`, `<`, `>`, `BETWEEN` and `ORDER BY`.

### The price of an index

An index is not free.

- It takes disk space.
- Every `INSERT`, `UPDATE`, `DELETE` must also update the index, so **writes get slower**.

So: index the columns you **search, join and sort** on. Do not index everything.

### Composite indexes

An index on two columns:

```sql
CREATE INDEX idx_orders_user_status ON orders (user_id, status);
```

Column **order matters**. Think of a phone book sorted by last name, then first name. You can look up by last name, or last + first name. You cannot look up by first name alone.

So this index helps `WHERE user_id = 7` and `WHERE user_id = 7 AND status = 'paid'`, but not `WHERE status = 'paid'` alone.

Put the column you filter with `=` most often first.

### Covering index and unique index

- A **covering index** contains every column the query needs, so the database never visits the table. `CREATE INDEX ... ON orders (user_id) INCLUDE (total);`
- A **unique index** also blocks duplicates. A `UNIQUE` constraint creates one.

### When the database ignores your index

- The table is small. Reading it all is faster.
- You wrap the column in a function: `WHERE lower(email) = 'a@x.com'` cannot use a plain index on `email`. Create an index on `lower(email)`.
- You search with a leading wildcard: `LIKE '%abc'`.
- The query returns most of the table anyway.

## Reading EXPLAIN ANALYZE

`EXPLAIN ANALYZE` runs the query and shows how Postgres did it.

```sql
EXPLAIN ANALYZE SELECT * FROM orders WHERE user_id = 7;
-- -> Seq Scan on orders  (cost=0.00..18334.00 rows=52 ...) (actual time=0.02..95.4 ...)
-- ->   Filter: (user_id = 7)
-- -> Execution Time: 95.6 ms
```

After the index:

```sql
-- -> Index Scan using idx_orders_user_id on orders  (actual time=0.03..0.05 ...)
-- -> Execution Time: 0.09 ms
```

| You see | It means |
| --- | --- |
| `Seq Scan` | read the whole table (slow on big tables) |
| `Index Scan` / `Index Only Scan` | used an index (good) |
| `actual time` | real milliseconds |
| `rows=` | how many rows were returned or estimated |

> Rule: do not guess. Measure with `EXPLAIN ANALYZE` before and after.

## The N+1 problem

Say you show 20 orders, and next to each order, the user's name.

The slow way: **1** query for the orders, then **N** (20) queries, one per order, to get each user.

@@ vflow | Figure 4.3: N+1 queries, in a loop.
1 query|SELECT * FROM orders LIMIT 20|blue -then, for each order-> 20 more queries|SELECT * FROM users WHERE id = ?   (x 20)|red
@@ end

That is 21 round trips. If each costs 2 ms, it is 42 ms. With 1,000 orders it is 2 seconds. And you never see an error, only a slow page.

The fix: **one** query that brings everything.

```sql
SELECT o.id, o.item, u.name
FROM orders o
JOIN users u ON u.id = o.user_id
LIMIT 20;
```

Or two queries (`SELECT ... WHERE id IN (1, 2, 3, ...)`). Both are fixed counts, not growing with N.

::: {.box .fastapi}
**How FastAPI does this**

With SQLAlchemy, N+1 happens when you loop over `orders` and touch `order.user`, and each touch runs a query. Fix it by loading with the query: `selectinload(Order.user)` or `joinedload(Order.user)`. With async SQLAlchemy, lazy loading is not allowed at all, so you are forced to load on purpose. Alembic creates your indexes: `op.create_index(...)`.
:::

## Common mistakes

::: {.box .mistake}
**Common mistakes**

- Using `FLOAT` for money. Use `NUMERIC`, or store whole cents as an integer.
- Copying the same fact in many tables, then forgetting to update one.
- No index on a foreign key column that you filter by.
- Adding too many indexes and slowing down writes.
- Wrong column order in a composite index.
- Not noticing N+1, because the code "works".
:::

## Interview corner

::: {.box .interview}
**Interview corner**

**Q: What is normalization? Why denormalize?**
Storing each fact once, to avoid mismatched copies. Denormalize only to make a measured slow read faster, accepting extra work to keep copies in sync.

**Q: How does an index speed up a query? What does it cost?**
It is a sorted structure (B-tree) that lets the database jump to rows instead of scanning all of them. It costs disk space and slows writes.

**Q: Why does column order matter in a composite index?**
The index is sorted by the first column, then the second. A query can use it only from the left side. An index on `(a, b)` helps `a` and `a, b`, not `b` alone.

**Q: What is the N+1 problem and how do you fix it?**
One query for a list, then one more per item. Fix with a join or batch loading (`IN (...)`, `selectinload`).

**Q: A query is slow. What do you do?**
Run `EXPLAIN ANALYZE`, look for a `Seq Scan` on a big table, add or fix an index, re-measure.
:::

## Exercises

::: {.box .exercise}
**Exercises**

1. Design tables for a blog: users, posts, comments, tags (a post has many tags, a tag has many posts). List the tables, the keys and which are join tables.
2. A table `orders` has the column `customer_city`. Explain what goes wrong when a customer moves, and how to fix the design.
3. You have an index on `(country, city)`. Which of these use it: `WHERE country = 'IN'`, `WHERE city = 'Pune'`, `WHERE country = 'IN' AND city = 'Pune'`?
4. `EXPLAIN ANALYZE` shows a `Seq Scan` taking 300 ms on 5 million rows. List 3 things you would check or do.
5. An endpoint returns 50 posts with the author name and takes 2 seconds. Explain a likely cause and the fix.
6. **Think:** why is a unique index useful beyond speed?
:::
