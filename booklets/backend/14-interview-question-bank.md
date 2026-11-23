# 14. Interview question bank

Short questions with short answers, grouped by topic. Cover the answer, say yours out loud, then compare. A good interview answer has three parts: **a one-line definition, a reason or example, and a trade-off.**

## HTTP and APIs

**1. What happens when you type a URL and press Enter?**
The browser finds the IP address (DNS), opens a connection (TCP, then TLS for HTTPS), sends an HTTP request, the server (often behind a load balancer) runs code and replies, and the browser renders the response.

**2. What makes an API RESTful?**
Resources as nouns in URLs, HTTP methods as verbs, stateless requests, standard status codes, JSON bodies.

**3. How do you design pagination for a feed that changes quickly?**
Cursor-based pagination, because offsets shift when rows are added.

**4. How do you version an API?**
A version in the path (`/v1`), keep old versions alive for a while, and only add optional fields without a new version.

**5. How would you make a payment endpoint safe to retry?**
An idempotency key stored with the result.

**6. What is CORS?**
A browser rule that blocks a page from calling another origin unless the server allows it with headers. It does not protect the API from non-browser clients.

## Databases

**7. How do you find why a query is slow?**
`EXPLAIN ANALYZE`, look for a `Seq Scan` on a large table, add or fix an index, measure again.

**8. When would an index not help?**
Tiny tables, a function on the column, a leading wildcard `LIKE '%x'`, or a query that returns most rows.

**9. Explain the N+1 problem.**
One query for a list plus one per item. Fix with a join or an `IN` batch.

**10. What is a transaction? What is ACID?**
A group of steps that is all-or-nothing. Atomicity, Consistency, Isolation, Durability.

**11. How do you avoid a lost update?**
An atomic `UPDATE ... SET n = n + 1`, a row lock (`FOR UPDATE`), or a version column.

**12. Normalization vs denormalization?**
Normalize to avoid mismatched copies. Denormalize only to speed up a measured slow read.

**13. How do you scale reads on a database?**
Add an index, cache, read replicas, and only then think about sharding.

**14. SQL or NoSQL for a new project?**
Start with Postgres. Add other stores for a clear reason: cache, search, vectors, huge scale.

**15. Find the top 3 orders per user.**
`ROW_NUMBER() OVER (PARTITION BY user_id ORDER BY total DESC)` in a CTE, then `WHERE rn <= 3`.

## Auth and security

**16. How do you store passwords?**
A salted, slow hash (bcrypt or argon2). Never plain text.

**17. Sessions or JWT?**
Sessions: easy to revoke, need shared storage. JWT: stateless and scalable, but hard to revoke, so use short access tokens and refresh tokens.

**18. How do you stop users from seeing each other's data?**
Check ownership on every request that touches a record (prevents IDOR).

**19. What is CSRF and XSS?**
XSS: injected script runs in your page and can steal data. CSRF: another site makes the browser send a request with your cookie. Use `HttpOnly` and `SameSite` cookies and CSRF tokens.

**20. A key was pushed to GitHub. What do you do?**
Revoke and rotate it at once. Removing the commit does not help, because it was copied.

## Performance and scale

**21. How would you speed up a slow endpoint?**
Measure first (trace, `EXPLAIN`). Then fix queries and indexes, remove N+1, cache, move slow work to a queue, add concurrency.

**22. Explain cache-aside and its risks.**
Read cache, fill on a miss with a TTL. Risks: stale data and stampede. Use TTLs, delete on write, locks, and jitter.

**23. What is a cache stampede?**
Many requests rebuild an expired popular key at once. Use locks, jitter or early refresh.

**24. When do you use a queue?**
For slow work, traffic spikes, retries and isolation. Return `202` and let workers finish.

**25. What does idempotent mean for a job and why does it matter?**
Running it twice has the same result as once. Queues deliver at least once, so jobs may run twice.

**26. Compare token bucket and fixed window.**
Token bucket allows controlled bursts with a steady average. Fixed window is simpler but can allow a double burst at the edge.

**27. Why do you need a connection pool?**
Opening connections is costly and databases allow few. A pool reuses them.

**28. What does blocking the event loop do?**
It freezes all requests on that worker.

**29. What is backpressure?**
Slowing or rejecting new work when full: limits, bounded queues, timeouts, load shedding.

**30. What is a circuit breaker?**
After repeated failures it stops calling a dependency, fails fast, then tests it again later.

## Design and operations

**31. Why a stateless server?**
Any copy can serve any request, so you can scale out and survive crashes.

**32. What do you log, and what never?**
Log events with request ids in structured form. Never passwords, tokens or personal data.

**33. Why use p99?**
Averages hide slow outliers. p99 shows the worst 1%.

**34. Liveness vs readiness?**
Alive: restart if not. Ready: send traffic only if yes.

**35. What goes in a service layer?**
Business rules and coordination, no HTTP and no SQL.

**36. How do you handle two LLM providers?**
An interface, an adapter per provider, a factory, plus retries and fallbacks.

## Scenario questions

**37. Your API suddenly gets slow. What do you check first?**
Dashboards (rate, errors, p95), recent deploys, database load and slow queries, connection pool use, queue length, external API latency. Use traces to find the slow span.

**38. Your database CPU is at 100%.**
Find the top queries, check for missing indexes and N+1, add caching, kill runaway queries, then plan replicas.

**39. An LLM feature is slow and expensive. What do you do?**
Stream the answer, cache (also semantic cache), use a smaller model for easy cases, limit tokens, move heavy work to a queue, and set per-user limits.

**40. Users report seeing someone else's data.**
Suspect missing ownership checks, a shared cache key without the user id, or state kept in a global variable. Fix, then audit.

**41. A job charged customers twice.**
The job was not idempotent and was retried. Add an idempotency key or a unique constraint, and a state check.

**42. Design a URL shortener, briefly.**
`POST /shorten` stores a short code and the long URL in a table with a unique index on the code. `GET /{code}` looks it up (cache first) and returns a `301` or `302`. Make codes with a counter or random base62. Add rate limits and expiry. (Full design in the System Design booklet.)

## Questions to ask them

Interviews go both ways. Good questions: "How do you handle deploys and rollbacks?", "What does on-call look like?", "How do you monitor the services?", "What is the hardest technical problem the team has now?"
