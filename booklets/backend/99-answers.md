# Answers to the exercises

Try each exercise first. Then compare. For "Think" questions, your own reasoning matters more than the exact words.

## Chapter 1: How a backend works

1. Client: the app or browser. It sends the request and shows the page. Server: checks who the user is, loads their data and builds the answer. Database: stores the profile.
2. Hiding a button is not security. Anyone can send the request by hand. The server must check the user's role on every admin request.
3. The second server has no memory of the login. The user's next request may land there and be told "please log in", at random. Fix: keep login state in a shared store (database or Redis) or in a token.
4. The client only shows things, so it can differ per user. The rules protect data and money, so they must be the same for everyone, and only the server can enforce them.
5. In the database, usually with a cached copy in Redis. Client memory is lost when the app closes and is different for every user. Server memory is lost on restart and not shared between server copies.

## Chapter 2: HTTP and REST

1. (a) `GET /users/{id}/comments` (b) `POST /posts/{id}/comments` (c) `PATCH /comments/{id}` (d) `DELETE /comments/{id}`.
2. The server may have processed the first request. A retry could charge twice. With an idempotency key, the server sees the same key, returns the stored result, and does not charge again.
3. (a) `401` (b) `403` (c) `409` (d) `422` (e) `500`.
4. `GET /users/5`, `DELETE /orders/9`, `GET /orders`.
5. After the client loads page 1, new posts push everything down. The item that was last on page 1 is now at the start of page 2. Cursor pagination avoids this.

## Chapter 3: SQL and Postgres

1. `SELECT name FROM users WHERE city = 'Pune';`
2. ```sql
   SELECT u.name, COALESCE(SUM(o.total), 0) AS spent
   FROM users u
   LEFT JOIN orders o ON o.user_id = u.id
   GROUP BY u.id, u.name;
   ```
3. With `HAVING`: `SELECT user_id, SUM(total) FROM orders GROUP BY user_id HAVING SUM(total) > 100;`. With a CTE: put the `GROUP BY` in `WITH spend AS (...)` and then `SELECT ... FROM spend WHERE spent > 100`.
4. ```sql
   WITH r AS (
     SELECT user_id, item, total,
            ROW_NUMBER() OVER (PARTITION BY user_id ORDER BY total DESC) AS rn
     FROM orders)
   SELECT * FROM r WHERE rn = 1;
   ```
5. `WHERE` runs before `SELECT`, so the alias `n` does not exist yet. Use `WHERE name = 'Asha'`.
6. Order `13` points to a user that does not exist (an orphan row). A **foreign key constraint** prevents it.

## Chapter 4: Schema design, indexes, N+1

1. Tables: `users(id)`, `posts(id, user_id)`, `comments(id, post_id, user_id)`, `tags(id, name)`. Join table: `post_tags(post_id, tag_id)` with a composite primary key.
2. If a customer moves, you must update every order. Miss one and the data disagrees. Fix: keep the city in a `customers` table, and have `orders` hold only `customer_id`.
3. `WHERE country = 'IN'`: yes. `WHERE city = 'Pune'`: no. `WHERE country = 'IN' AND city = 'Pune'`: yes.
4. Check: is there an index on the filtered column; is a function wrapped around the column; does the query return most of the table; are the statistics fresh. Then add a fitting index, select fewer columns, and re-measure with `EXPLAIN ANALYZE`.
5. Likely N+1: one query per post to load the author. Fix with a join, or batch loading (`selectinload`).
6. A unique index also **guarantees no duplicates**, even when two requests arrive at the same time. The database enforces the rule, not your code.

## Chapter 5: Transactions

1. Both read "1 ticket left" and both sell it, so you oversell. Prevent with `SELECT ... FOR UPDATE`, or an atomic `UPDATE tickets SET left = left - 1 WHERE id = ? AND left > 0`, or a version column, or a unique constraint on the seat.
2. (a) Durability (b) Consistency (c) Atomicity.
3. The transaction holds locks and a connection for 5 seconds, so others wait and the pool may run out. Also the payment may succeed while the write fails. Do the slow call outside the transaction.
4. A deadlock. Fix: always update rows in the same order (1 then 2), and keep transactions short.
5. When correctness across several rows is critical (money, inventory) and you accept retrying on conflict.

## Chapter 6: SQL vs NoSQL

1. (a) key-value (Redis) (b) relational (Postgres) (c) graph (d) a document store, or Postgres with `JSONB`.
2. `SELECT settings->>'color' FROM my_table;`
3. You lose constraints and foreign keys, queries and indexes get hard, the data shape drifts, and a small change rewrites a huge blob.
4. Postgres (users, chats, metadata), a vector store or `pgvector` (embeddings), Redis (cache, rate limits), object storage (original files), a queue (ingestion jobs).
5. It is mature, has strong transactions, rich SQL, `JSONB` and `pgvector`, so it covers many needs, and you run fewer systems.

## Chapter 7: Authentication and authorization

1. SHA-256 is fast, so attackers try billions of guesses per second, and without a salt, equal passwords share a hash. Use bcrypt or argon2 with a salt.
2. No. The signature is made with the server's secret key. A changed payload no longer matches the signature, and the server rejects the token.
3. A stolen token works for 7 days and cannot be revoked. Use a short access token (about 15 minutes) and a refresh token that the server can revoke.
4. IDOR (broken object-level authorization). Check that the invoice belongs to the current user. Return `403` or `404`.
5. Website: a session cookie with `HttpOnly`, `Secure`, `SameSite`, and CSRF protection. Mobile app: a token in the `Authorization` header, kept in secure storage. JWT in JavaScript storage on a website is exposed to XSS.
6. The password goes only to Google. You never store or hash it, so you avoid leaks, and Google handles MFA and attack detection.

## Chapter 8: Caching and Redis

1. Key `top_products:v1`, TTL 30 to 60 seconds. On a product change, delete the key (or just accept up to one TTL of staleness). Add a lock or TTL jitter to avoid a stampede. 500 requests per second at 80 ms is a heavy load, so one rebuild per TTL is a huge saving.
2. The id makes the key unique per user. `profile` would give every user the same profile.
3. Delete the key when the name is updated (invalidate on write), or update the cached value on write, or use a shorter TTL.
4. Example: a popular key expires and 1,000 requests rebuild it at once, overloading the database. Prevention: a lock so only one request rebuilds it.
5. Leaderboard: sorted set. Login counter: string with `INCR`. Unique visitors: set. User object: hash (or a JSON string).
6. User A's orders get cached under `GET:/orders`, and user B gets them. Put the user id in the key, or do not cache private data in a shared cache.

## Chapter 9: Queues and workers

1. The API saves the file, creates a job and returns `202` with a `job_id`. The worker parses, chunks and calls the LLM, then saves the summary. The user polls `GET /jobs/{id}` (or gets a push). Add retries and a dead-letter queue.
2. Store a unique key such as `welcome_email_sent:{user_id}`. The job checks it first and skips if it already exists.
3. Up to 5 attempts. Wait 1, 2, 4, 8 seconds with random jitter, and obey `Retry-After` if present. After the last failure, move the job to a dead-letter queue.
4. (a) queue (b) pub/sub.
5. Running it twice adds the money twice. Safer: "mark payment `P123` as paid", guarded by a unique payment id.
6. Add more workers, find and fix slow or failing jobs, limit the producers (bounded queue or rate limit), and check for jobs that fail and loop.

## Chapter 10: Rate limiting

1. 60 requests at 12:00:59 (end of window one), then 60 more at 12:01:00 (start of window two). That is 120 within 2 seconds, and no window is broken.
2. 5 pass and 3 are rejected. Over the next 3 seconds, 3 tokens refill, so the 3 new requests pass.
3. (a) IP and the account name (b) API key (c) IP.
4. Up to about 400 per minute, because each server counts alone. Fix: keep counters in shared Redis.
5. LLM calls cost money and are slow, so a few heavy users could drain your budget or block others.

## Chapter 11: Concurrency, pooling, backpressure

1. (a) I/O-bound, use async (b) CPU-bound, use multiple processes (c) I/O-bound, use async or threads.
2. 8 x 20 = 160 connections wanted, but Postgres allows 100, so connections fail or wait. Lower `pool_size` (for example 8 to 10 per worker), or use PgBouncer.
3. The whole worker is frozen for 5 seconds. Every other request on that worker waits.
4. Retries with backoff handle short blips. After many failures the circuit breaker opens and calls fail fast, so you do not waste time. A fallback (cached data, another provider, or a queued retry) keeps the feature working. Half-open tests recovery.
5. A fast `503` protects the system and keeps it healthy for the remaining users. Trying to serve everyone can make all requests slow, then fail.

## Chapter 12: Observability and security

1. `{"time": "...", "level": "WARNING", "msg": "login failed", "user_id": 7, "ip": "1.2.3.4", "request_id": "a1b2"}`. Never include the password.
2. p95 and p99 latency, plus the error rate. Averages hide the slow tail that users feel.
3. The LLM call takes 950 ms. Options: stream the answer, use a smaller or faster model, shorten the prompt, cache.
4. IDOR (broken object-level authorization). Check that the invoice belongs to the current user.
5. Mass assignment: the server saved a field the client should never set. Use a request schema without `is_admin` (and `extra="forbid"`), and set roles on the server.
6. No. The key stays in git history and may already be copied. Revoke and rotate it.

## Chapter 13: Clean layers and patterns

1. (a) service (b) repository (c) route (d) service (it calls an emailer that was passed in).
2. The route reads and validates input and calls a service. The service holds the rules. The repository holds the SQL. Schemas define the input and output shapes.
3. The **strategy** pattern: one interface (`pay`) with one class per method, chosen by a dictionary lookup. Adding a method means adding a class.
4. The service must not know about HTTP, so it can be reused by workers and scripts. The API layer translates `OutOfStock` into a `409`.
5. `LLMClient` has `chat(messages) -> str`. `GroqAdapter` and `OpenAIAdapter` implement it with their own SDK. The service calls `client.chat(...)` only.
6. For a tiny script or a prototype, where the extra layers cost more than they give. Add structure as the project grows.
