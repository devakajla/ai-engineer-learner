# 3. SQL and Postgres

Most apps keep their important data in a **relational database**, and **SQL** is the language you use to ask questions to it. Postgres is the most popular open-source relational database, and the one most AI engineers use (it can even store embeddings with `pgvector`).

This chapter is about *thinking* in SQL. We use one small data set all through it.

## Tables, rows, keys

A **table** is a grid. Each **row** is one item. Each **column** is one fact about it.

**users**

| id | name | city |
| --- | --- | --- |
| 1 | Asha | Pune |
| 2 | Ravi | Delhi |
| 3 | Meera | Pune |

**orders**

| id | user_id | item | total |
| --- | --- | --- | --- |
| 10 | 1 | Laptop | 900 |
| 11 | 1 | Mouse | 20 |
| 12 | 2 | Phone | 500 |
| 13 | 4 | Book | 15 |

- **Primary key** (`id`): a value that is unique for every row. It names the row.
- **Foreign key** (`user_id`): a column that points to the primary key of another table. It is how tables are linked.

Look at order `13`: it points to user `4`, who does not exist. A real foreign key rule would block that row. We keep it here to show joins.

## Reading data: SELECT

```sql
SELECT name, city FROM users WHERE city = 'Pune' ORDER BY name;
-- -> Asha | Pune
-- -> Meera | Pune
```

Read it as a sentence: *pick these columns, from this table, keep rows where this is true, sort like this.*

Useful pieces: `WHERE` (filter rows), `ORDER BY ... DESC`, `LIMIT 10`, `DISTINCT`, `LIKE 'A%'`, `IN (1, 2)`, `BETWEEN 10 AND 20`, `IS NULL`.

> `NULL` means "unknown". It is not zero and not an empty string. `x = NULL` is never true; write `x IS NULL`.

## Joins: combining tables

A join puts rows from two tables side by side when a condition matches.

```sql
SELECT u.name, o.item, o.total
FROM users u
JOIN orders o ON o.user_id = u.id;
-- -> Asha  | Laptop | 900
-- -> Asha  | Mouse  | 20
-- -> Ravi  | Phone  | 500
```

Meera has no orders, and order 13 has no user, so neither appears. That is an **INNER JOIN**: only matches.

@@ grid 2 | Figure 3.1: the four joins, in words. A = left table, B = right table.
INNER JOIN|only rows that match in both A and B;(Asha, Ravi)|green
LEFT JOIN|all rows of A, plus matches from B;rows with no match get NULL;(Asha, Ravi, Meera)|blue
RIGHT JOIN|all rows of B, plus matches from A;(Asha, Ravi, order 13)|yellow
FULL JOIN|everything from both sides|purple
@@ end

```sql
SELECT u.name, o.item
FROM users u
LEFT JOIN orders o ON o.user_id = u.id;
-- -> Asha  | Laptop
-- -> Asha  | Mouse
-- -> Ravi  | Phone
-- -> Meera | NULL
```

> Use `LEFT JOIN` when you want "all users, even those with no orders".

## Grouping: GROUP BY and HAVING

To count or add up many rows into one, you **group** them.

```sql
SELECT user_id, COUNT(*) AS orders, SUM(total) AS spent
FROM orders
GROUP BY user_id;
-- -> 1 | 2 | 920
-- -> 2 | 1 | 500
-- -> 4 | 1 | 15
```

Common aggregate functions: `COUNT`, `SUM`, `AVG`, `MIN`, `MAX`.

`WHERE` filters rows **before** grouping. `HAVING` filters groups **after**.

```sql
SELECT user_id, SUM(total) AS spent
FROM orders
GROUP BY user_id
HAVING SUM(total) > 100;
-- -> 1 | 920
-- -> 2 | 500
```

The order SQL runs things in is not the order you write it:

@@ flow | Figure 3.2: the real order of work inside a query.
FROM + JOIN|build the rows|blue -> WHERE|keep rows|green -> GROUP BY|make groups|yellow -> HAVING|keep groups|purple -> SELECT + ORDER|pick and sort|gray
@@ end

This is why you cannot use a `SELECT` alias inside `WHERE`: `WHERE` runs earlier.

## Subqueries and CTEs

A **subquery** is a query inside a query.

```sql
SELECT name FROM users
WHERE id IN (SELECT user_id FROM orders WHERE total > 400);
-- -> Asha
-- -> Ravi
```

A **CTE** (`WITH`) gives a name to a step, so long queries read top to bottom like a story.

```sql
WITH spend AS (
  SELECT user_id, SUM(total) AS spent
  FROM orders
  GROUP BY user_id
)
SELECT u.name, s.spent
FROM spend s
JOIN users u ON u.id = s.user_id
WHERE s.spent > 100;
-- -> Asha | 920
-- -> Ravi | 500
```

> Prefer CTEs over deep nested subqueries. They are much easier to read and to debug.

## Window functions

A window function does a calculation across related rows **without collapsing them** into one row (unlike `GROUP BY`).

```sql
SELECT user_id, item, total,
       ROW_NUMBER() OVER (PARTITION BY user_id ORDER BY total DESC) AS rn
FROM orders;
-- -> 1 | Laptop | 900 | 1
-- -> 1 | Mouse  | 20  | 2
-- -> 2 | Phone  | 500 | 1
-- -> 4 | Book   | 15  | 1
```

`PARTITION BY` makes a separate window per user. `ORDER BY` inside decides the order within it.

| Function | What it gives |
| --- | --- |
| `ROW_NUMBER()` | 1, 2, 3, ... unique position, ties broken arbitrarily |
| `RANK()` | ties share a rank, then a gap (1, 1, 3) |
| `DENSE_RANK()` | ties share a rank, no gap (1, 1, 2) |
| `SUM(x) OVER (ORDER BY ...)` | running total |
| `LAG(x)` / `LEAD(x)` | value from the previous / next row |

Classic task: "the top order of each user" is `ROW_NUMBER() ... WHERE rn = 1` (put the query in a CTE first, then filter `rn = 1`).

Running total:

```sql
SELECT id, total, SUM(total) OVER (ORDER BY id) AS running
FROM orders;
-- -> 10 | 900 | 900
-- -> 11 | 20  | 920
-- -> 12 | 500 | 1420
-- -> 13 | 15  | 1435
```

## Changing data

```sql
INSERT INTO users (name, city) VALUES ('Kabir', 'Goa');
UPDATE users SET city = 'Mumbai' WHERE id = 2;
DELETE FROM orders WHERE id = 13;
```

> **Always** write a `WHERE` on `UPDATE` and `DELETE`. Without it, you change every row.

::: {.box .fastapi}
**How FastAPI does this**

FastAPI does not talk SQL by itself. You use **SQLAlchemy 2.0** (async), which turns Python code into SQL, and **Alembic** to change the table structure safely over time. A route asks a repository for rows, and the repository runs the SQL. Learning the raw SQL above helps you read what SQLAlchemy actually sends.
:::

## Common mistakes

::: {.box .mistake}
**Common mistakes**

- Forgetting `WHERE` on `UPDATE` or `DELETE`.
- Using `= NULL` instead of `IS NULL`.
- Using `WHERE` when you meant `HAVING` (filter after grouping).
- Using `SELECT *` in application code. It breaks when columns change and sends extra data.
- Using an `INNER JOIN` when you needed a `LEFT JOIN`, so rows silently disappear.
- Building SQL by joining strings with user input. This is **SQL injection** (chapter 12). Always use parameters.
:::

## Interview corner

::: {.box .interview}
**Interview corner**

**Q: What is the difference between `WHERE` and `HAVING`?**
`WHERE` filters rows before grouping. `HAVING` filters groups after aggregation.

**Q: INNER JOIN vs LEFT JOIN?**
Inner keeps only matching rows. Left keeps every row from the left table and fills `NULL` where the right side has no match.

**Q: `RANK` vs `DENSE_RANK` vs `ROW_NUMBER`?**
`ROW_NUMBER` is always unique. `RANK` repeats on ties and skips numbers. `DENSE_RANK` repeats on ties and does not skip.

**Q: What is a CTE and why use it?**
A named temporary result inside one query (`WITH ...`). It makes complex queries readable.

**Q: Find the second highest salary.**
Use `DENSE_RANK() OVER (ORDER BY salary DESC)` in a CTE and keep rank 2. Or `SELECT MAX(salary) FROM t WHERE salary < (SELECT MAX(salary) FROM t)`.
:::

## Exercises

::: {.box .exercise}
**Exercises**

Use the `users` and `orders` tables from this chapter.

1. Write a query for the names of all users who live in Pune.
2. Write a query that shows each user's name and total money spent. Users with no orders must show `0` (hint: `LEFT JOIN`, `COALESCE`).
3. Find users who spent more than 100 in total. Do it once with `HAVING` and once with a CTE.
4. For each user, show their most expensive order using `ROW_NUMBER()`.
5. Explain why `SELECT name AS n FROM users WHERE n = 'Asha'` fails.
6. **Think:** why does order `13` (pointing to user `4`) show a problem with the design, and which database feature prevents it?
:::
