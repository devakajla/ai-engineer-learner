# 8. Caching and Redis

A **cache** is a quick-access copy of data that is slow to get. You keep the answer close, so you do not repeat the slow work.

Real life: you keep your water bottle on your desk instead of walking to the kitchen each time.

Caching is one of the biggest speed-ups in backends, and also one of the biggest sources of bugs. The famous joke: *"There are only two hard things in computer science: cache invalidation and naming things."*

## Where caches live

@@ flow | Figure 8.1: layers of cache, closest to the user first.
Browser|cached files|blue -> CDN|copies near the user|green -> App cache|Redis or memory|red -> Database|the truth, slowest|yellow
@@ end

A request is answered by the first layer that has the data. Each layer you skip saves time.

## Why cache? The numbers

| Source | Rough time |
| --- | --- |
| Python dict in memory | microseconds |
| Redis (same network) | about 1 millisecond |
| Postgres query | 1 to 50 milliseconds |
| Slow query or an LLM call | 100 ms to many seconds |

If 1,000 users ask for the same product page, run the query once, and serve 999 from cache.

## The cache-aside pattern

The most common pattern. The app manages the cache.

@@ vflow | Figure 8.2: cache-aside (also called lazy loading).
1. Check the cache|key = "product:42"|blue -hit: return it. miss: go on-> 2. Read the database|SELECT ... WHERE id = 42|yellow -> 3. Save to cache with a TTL|SET product:42 data EX 300|green -> 4. Return the answer|the next request will be a hit|purple
@@ end

```python
def get_product(pid):
    data = cache.get(f"product:{pid}")
    if data:                       # cache hit
        return json.loads(data)
    row = db.query_product(pid)    # cache miss
    cache.set(f"product:{pid}", json.dumps(row), ex=300)
    return row
```

## Other write strategies

| Strategy | How it works | Good | Bad |
| --- | --- | --- | --- |
| **Cache-aside** | app reads cache, fills it on a miss | simple, popular | first read is slow; data can go stale |
| **Write-through** | write to cache and database together | cache always fresh | slower writes |
| **Write-behind** | write to cache, save to database later | fast writes | data loss risk if the cache dies |

## TTL: time to live

A **TTL** gives each cached item an expiry. After it, the item is deleted.

TTL is your safety net. Even if you forget to invalidate, stale data lasts at most one TTL. Pick it by asking "how old may this data be?": a stock price 1 second, a product page 5 minutes, a country list 1 day.

## Invalidation: when data changes

When the real data changes, the cache copy is wrong (stale). Options:

1. **Wait for TTL.** Simple, slightly stale.
2. **Delete on write.** After updating the database, `DEL product:42`. The next read refills it.
3. **Update on write.** Write the new value to cache too.

> Delete is usually safer than update, because it avoids writing a wrong value after a race.

## Cache stampede

A popular key expires. In the same moment, 1,000 requests miss and **all** hit the database. The database may fall over. This is a **stampede** (or thundering herd).

@@ grid 3 | Figure 8.3: three ways to fight a stampede.
Lock|only one request rebuilds the value;the others wait or serve old data|blue
Jitter|add a random bit to each TTL;keys do not all expire together|green
Early refresh|refresh the key a little before it expires|yellow
@@ end

## Eviction: when the cache is full

Memory is limited. When full, Redis removes something. The policy decides what.

| Policy | Removes |
| --- | --- |
| `allkeys-lru` | the least recently used key (a good default for caches) |
| `allkeys-lfu` | the least frequently used key |
| `volatile-ttl` | the key closest to expiry |
| `noeviction` | nothing; writes fail when full |

## Redis

**Redis** is an in-memory data store. It is very fast, and it is the most used cache. It is also used for sessions, rate limits, queues and pub/sub. Everything lives in RAM, and it can save to disk.

Data types and what they are for:

| Type | Example commands | Use |
| --- | --- | --- |
| String | `SET k v EX 60`, `GET k`, `INCR k` | cache, counters |
| Hash | `HSET user:1 name Asha`, `HGETALL user:1` | objects |
| List | `LPUSH q job`, `BRPOP q 0` | simple queue |
| Set | `SADD tags a b`, `SISMEMBER tags a` | unique items |
| Sorted set | `ZADD board 90 asha`, `ZRANGE board 0 2` | leaderboards |
| Pub/Sub | `PUBLISH ch msg`, `SUBSCRIBE ch` | live messages |

Key naming habit: `entity:id:field`, such as `user:7:profile`.

```
SET product:42 '{"name":"Laptop"}' EX 300
GET product:42
-- -> {"name":"Laptop"}
TTL product:42
-- -> 297
```

### Persistence

| Mode | How | Note |
| --- | --- | --- |
| RDB | snapshot every few minutes | fast restart, can lose the last minutes |
| AOF | logs every write | safer, bigger files |

For a pure cache you may not need persistence at all.

### Distributed lock

When several servers must not do the same job at once (for example, rebuild one cache key), a lock in Redis helps.

```
SET lock:rebuild:42 token NX EX 10
-- NX: only set if it does not exist. EX 10: expires in 10 s (in case we crash)
```

If it returns OK, you hold the lock. Release it with the same token. Always set an expiry.

## HTTP caching: ETag and Cache-Control

Caching also lives in HTTP itself.

```
Cache-Control: public, max-age=300     # any cache may keep it 5 minutes
ETag: "v42"                            # fingerprint of this version
```

Next time, the client sends `If-None-Match: "v42"`. If nothing changed, the server answers `304 Not Modified` with no body. This saves bandwidth. Never cache private data (`Cache-Control: private` or `no-store`).

## Semantic caching for LLMs

LLM calls are slow and cost money. A normal cache only helps if the question is **exactly** the same. A **semantic cache** compares the *meaning* of the question (using embeddings). "How do I reset my password?" and "password reset steps" are different text but the same meaning, so one stored answer can serve both. You will build this in the GenAI booklet.

::: {.box .fastapi}
**How FastAPI does this**

You create one Redis client in the app `lifespan` and give it to routes with `Depends`. The cache-aside code above sits in a service function. The `fastapi-cache2` library gives a `@cache(expire=60)` decorator for simple cases. For HTTP caching, set `Cache-Control` and `ETag` headers on the `Response`.
:::

## Common mistakes

::: {.box .mistake}
**Common mistakes**

- Caching without a TTL, then serving old data forever.
- Forgetting to invalidate after a write.
- Caching private data under a shared key (user A sees user B's data). Put the user id in the key.
- Treating the cache as the source of truth.
- Letting a hot key expire at once for all users (stampede).
- Caching a failure (such as a `None` from a temporary error) for a long time.
:::

## Interview corner

::: {.box .interview}
**Interview corner**

**Q: Explain cache-aside.**
Check the cache. On a miss, read the database, store the result with a TTL, and return it. On writes, delete or update the cached key.

**Q: What is a cache stampede and how do you prevent it?**
Many requests rebuild an expired hot key at once and overload the database. Prevent with a lock, TTL jitter, or early refresh.

**Q: How do you keep cache and database consistent?**
You cannot be perfect. Use TTLs, delete the key on write, and accept a short window of stale data.

**Q: What is LRU?**
Least Recently Used: when full, remove the key that was used longest ago.

**Q: Why is Redis fast?**
It keeps data in memory, uses simple data structures and handles commands in a single fast loop.
:::

## Exercises

::: {.box .exercise}
**Exercises**

1. A page shows "top 10 products" and gets 500 requests per second. The query takes 80 ms. Design the cache: key name, TTL, and what happens when a product changes.
2. Why is `user:{id}:profile` a better key than `profile`?
3. Your cache TTL is 1 hour and a user edits their name. They still see the old name for up to an hour. Give two fixes.
4. Explain a stampede with one example and one prevention.
5. Which Redis type would you use for: a leaderboard, a login counter, a unique visitor set, a user object?
6. **Think:** what could go wrong if you cache a response that depends on the logged-in user, using the key `GET:/orders`?
:::
