# Quick Reference

Keep this part open while you code. Each table is a short reminder. The chapters explain the reasons.

## HTTP methods

| Method | Use it to | Has body? | Safe? | Idempotent? |
| --- | --- | --- | --- | --- |
| `GET` | read data | no | yes | yes |
| `POST` | create something new | yes | no | no |
| `PUT` | replace a whole item | yes | no | yes |
| `PATCH` | change part of an item | yes | no | usually no |
| `DELETE` | remove an item | no | no | yes |

> **Safe** means it does not change data. **Idempotent** means sending it 5 times leaves the same result as sending it once.

## Status codes you will use every week

| Code | Name | When |
| --- | --- | --- |
| `200` | OK | normal success |
| `201` | Created | a `POST` made a new item |
| `204` | No Content | success, nothing to send back (often `DELETE`) |
| `400` | Bad Request | the request is broken or makes no sense |
| `401` | Unauthorized | you are not logged in (no or bad credentials) |
| `403` | Forbidden | you are logged in but not allowed |
| `404` | Not Found | the item does not exist |
| `409` | Conflict | clashes with current state (duplicate email) |
| `422` | Unprocessable Entity | data has the wrong shape (FastAPI uses this for validation) |
| `429` | Too Many Requests | rate limit hit |
| `500` | Internal Server Error | a bug on the server |
| `503` | Service Unavailable | server is down or overloaded |

## SQL in one page

```sql
SELECT name, COUNT(*) AS n          -- pick columns
FROM orders o
JOIN users u ON u.id = o.user_id    -- combine tables
WHERE o.total > 100                 -- filter rows
GROUP BY name                       -- make groups
HAVING COUNT(*) > 2                 -- filter groups
ORDER BY n DESC                     -- sort
LIMIT 10 OFFSET 20;                 -- page
```

| Need | Write |
| --- | --- |
| add a row | `INSERT INTO t (a, b) VALUES (1, 2);` |
| change rows | `UPDATE t SET a = 5 WHERE id = 1;` |
| delete rows | `DELETE FROM t WHERE id = 1;` |
| keep unmatched left rows | `LEFT JOIN` |
| make a lookup fast | `CREATE INDEX idx_t_a ON t (a);` |
| see the query plan | `EXPLAIN ANALYZE SELECT ...;` |
| all-or-nothing change | `BEGIN; ... COMMIT;` (or `ROLLBACK;`) |

## Redis commands

| Command | What it does |
| --- | --- |
| `SET key value EX 60` | store a value that expires in 60 seconds |
| `GET key` | read it (nil if missing) |
| `DEL key` | delete it |
| `INCR key` | add 1 (good for counters and rate limits) |
| `EXPIRE key 30` | set or change the timer |
| `TTL key` | seconds left |
| `HSET user:1 name Dev` / `HGETALL user:1` | hash (like a small dict) |
| `LPUSH q job` / `BRPOP q 0` | list used as a queue |
| `SADD tags a b` / `SMEMBERS tags` | set |

## Patterns at a glance

| Problem | Pattern | Chapter |
| --- | --- | --- |
| Same data read again and again | cache-aside with a TTL | 8 |
| Slow work inside a request | put a job on a queue, return `202` | 9 |
| Too many requests from one user | token bucket or sliding window | 10 |
| Two users edit the same row | transaction or a version column | 5 |
| Many small queries in a loop | fix the N+1 problem with a join | 4 |
| Who may do what | check the user's role on every request | 7 |
