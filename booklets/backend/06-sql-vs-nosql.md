# 6. SQL vs NoSQL, and JSONB

For most apps, the right answer is **Postgres**. But the word "NoSQL" appears in every interview, and AI systems use special databases too (vector databases). You should know the map.

## Relational (SQL) databases

Data is in tables with a fixed structure (a schema). Tables link with keys. You query with SQL. You get strong transactions.

Examples: **Postgres**, MySQL, SQLite.

Strong at: money, orders, users, anything where facts must always agree.

## NoSQL: four families

"NoSQL" means "not only SQL". It is not one thing. It is a group of databases that choose a different shape for data.

@@ grid 2 | Figure 6.1: the four NoSQL families.
Key-value|key -> value, super fast lookup;Redis, DynamoDB;use: cache, sessions, counters|blue
Document|stores JSON-like documents;MongoDB, Firestore;use: flexible, nested data|green
Column family|wide rows, huge write volume;Cassandra, HBase;use: logs, time series at scale|yellow
Graph|nodes and relationships;Neo4j;use: social networks, recommendations|purple
@@ end

### A document store in one picture

```json
{
  "_id": "u7",
  "name": "Asha",
  "addresses": [{"city": "Pune"}, {"city": "Goa"}],
  "prefs": {"theme": "dark"}
}
```

Everything about a user sits in one document. Reads are fast (one lookup, no joins). The price: the same data repeated in many documents is hard to keep in sync, and joins across documents are weak.

## SQL vs NoSQL

| | SQL (Postgres) | NoSQL (document / key-value) |
| --- | --- | --- |
| Structure | fixed schema | flexible |
| Relationships | joins, foreign keys | embed or link by hand |
| Transactions | strong, multi-row | often weaker or limited |
| Scaling | vertical first; horizontal is harder | built to spread across many machines |
| Query power | SQL, very rich | simpler queries, depends on the DB |
| Best for | most business data | huge scale, simple access patterns, flexible shapes |

> Practical rule: **start with Postgres.** Move a part of your data to something else only when you have a clear reason: a cache (Redis), search (Elasticsearch), vectors (a vector DB), or massive scale.

## JSONB: flexibility inside Postgres

Postgres can store JSON in a column, with the type `JSONB` (binary JSON). You get a bit of NoSQL flexibility without leaving SQL.

```sql
CREATE TABLE events (
  id      SERIAL PRIMARY KEY,
  kind    TEXT NOT NULL,
  payload JSONB
);

INSERT INTO events (kind, payload)
VALUES ('click', '{"page": "/home", "user": {"id": 7}}');

SELECT payload->>'page' AS page FROM events;          -- text value
-- -> /home

SELECT * FROM events WHERE payload->'user'->>'id' = '7';
SELECT * FROM events WHERE payload @> '{"page": "/home"}';  -- contains
```

| Operator | Means |
| --- | --- |
| `->` | get a JSON part (stays JSON) |
| `->>` | get as text |
| `@>` | "contains" |

You can index it with a **GIN index**: `CREATE INDEX ON events USING GIN (payload);`.

When to use JSONB: data that changes shape a lot (settings, event details, an LLM's raw response). When not to: fields you always filter and join on. Make those real columns.

## Where vector databases fit

An AI app stores **embeddings** (lists of numbers that capture meaning) and searches "what is closest in meaning". This needs a vector index.

- **pgvector**: a Postgres extension. Your vectors live next to your normal data, in one database. Good default.
- **Qdrant, Weaviate, Pinecone, Chroma**: dedicated vector databases. More features and scale for big workloads.

You will meet this properly in the GenAI booklet.

## Polyglot persistence

Real systems often use several stores, each for what it is good at.

@@ flow | Figure 6.2: one app, several stores.
Postgres|users, orders, payments|blue -> Redis|cache, sessions, rate limits|red -> Vector DB|embeddings for search|purple -> Object storage|files, PDFs, images|yellow
@@ end

Each extra store means one more thing to run, back up and keep in sync. Add them slowly.

::: {.box .fastapi}
**How FastAPI does this**

A FastAPI app usually talks to Postgres through SQLAlchemy, to Redis with `redis-py`, and to a vector store through its client. Each connection is created once at startup (the `lifespan` function) and given to routes with `Depends`. A `JSONB` column is `Mapped[dict]` with SQLAlchemy's `JSONB` type.
:::

## Common mistakes

::: {.box .mistake}
**Common mistakes**

- Choosing MongoDB "because it is easy" and then needing joins and transactions everywhere.
- Putting everything in one giant `JSONB` column. You lose constraints and speed.
- Adding Redis, a vector DB and a queue on day one, before you need them.
- Treating a cache as the source of truth. A cache can be wiped. The database is the truth.
:::

## Interview corner

::: {.box .interview}
**Interview corner**

**Q: When would you pick NoSQL over SQL?**
When the access pattern is simple but the scale is huge, the data shape changes often, or you need very fast key lookups. Otherwise start with Postgres.

**Q: What are the types of NoSQL databases?**
Key-value (Redis), document (MongoDB), column-family (Cassandra), graph (Neo4j).

**Q: What is JSONB and when do you use it?**
A binary JSON column in Postgres. Use it for flexible, changing data like settings or event payloads, while keeping core fields as real columns.

**Q: Why can pgvector be enough for many AI apps?**
Your embeddings sit next to your normal data, with transactions and one system to run. A dedicated vector DB helps only at larger scale or for special features.
:::

## Exercises

::: {.box .exercise}
**Exercises**

1. Choose a database family for each: (a) a login session store, (b) bank balances, (c) "friends of friends" suggestions, (d) a shopping cart with flexible item options.
2. Write the SQL to read the field `color` out of a `JSONB` column `settings` (`{"color": "blue"}`).
3. A teammate wants to store the whole app in one `JSONB` column. Give 3 reasons to say no.
4. List the stores you would use for a RAG chatbot and what each holds.
5. **Think:** why is "start with Postgres" a good default?
:::
