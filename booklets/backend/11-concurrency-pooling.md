# 11. Concurrency, connection pools and backpressure

A busy backend gets many requests at the same time. **Concurrency** is how it deals with many things at once. This chapter explains the models, the limits, and what to do when the system is overloaded.

## Three ways to do many things at once

@@ grid 3 | Figure 11.1: processes, threads, async.
Processes|separate programs;own memory;true parallel on many cores;heavy|blue
Threads|inside one process;share memory;light;careful with shared data|green
Async|one thread, tasks take turns;switch while waiting;very light;best for waiting|yellow
@@ end

Most backend time is spent **waiting**: for the database, for another API, for disk. While one request waits, the CPU could serve another. That is the idea behind both threads and async.

### CPU-bound vs I/O-bound

| Type | Meaning | Example | Best tool |
| --- | --- | --- | --- |
| **I/O-bound** | mostly waiting | DB queries, API calls, LLM calls | async or threads |
| **CPU-bound** | mostly calculating | image resize, big maths, parsing | multiple processes |

> In Python, the **GIL** lets only one thread run Python code at a time, so threads do not speed up CPU-bound work. Processes do. For waiting, threads and async work well.

## The event loop (async in one picture)

An **event loop** is one worker who juggles many tasks. When a task has to wait (for a database answer), it steps aside, and the loop runs another task. When the answer arrives, the first task continues.

@@ flow | Figure 11.2: one thread, many requests.
Request A|asks the database;waits...|blue -> Loop|runs Request B|green -> Request B|asks the API;waits...|yellow -> Loop|A's data arrived, continue A|green
@@ end

The one deadly rule: **never block the loop.** If a task does slow work without waiting properly (a long loop, a `time.sleep`, a blocking library), the **whole server freezes**, for everyone.

## Workers in production

A production server runs several **worker processes**, and each can run async code inside.

```
gunicorn app.main:app -k uvicorn.workers.UvicornWorker -w 4
```

A common starting point is about one worker per CPU core. Each worker is a separate process with its own memory. That is another reason servers must be **stateless** (chapter 1).

## Connection pooling

Opening a database connection is **expensive**: a network handshake, a login, memory on the database. Doing it for every request is slow, and databases allow only a limited number of connections (Postgres often about 100).

A **connection pool** opens some connections once and **lends** them out.

@@ flow | Figure 11.3: the pool lends connections.
Requests|50 at once|blue -ask for one-> Pool|keeps 10 open connections;the rest wait in line|green -borrow and return-> Database|sees only 10 connections|yellow
@@ end

Key settings:

| Setting | Meaning |
| --- | --- |
| `pool_size` | connections kept open |
| `max_overflow` | extra connections allowed in a burst |
| `pool_timeout` | how long a request waits for a free connection |
| `pool_recycle` | close and replace old connections |

**Pool exhaustion**: every connection is busy, so new requests wait, then time out. The usual causes: slow queries, or code that **forgets to return** a connection (a session never closed), or a transaction held open during a slow API call.

The math to remember: `workers x pool_size` must stay below the database's connection limit. 4 workers with a pool of 20 is 80 connections already. For many connections, put **PgBouncer** between your app and Postgres.

## Race conditions

A **race condition** is a bug that depends on timing. Two requests read the same value and both write, as in chapter 5.

Tools against races: database transactions and constraints, atomic commands (`INCR`), locks, and idempotency. Do not rely on "it is unlikely".

## Timeouts: the most important setting

Every call that leaves your process needs a **timeout**: database, HTTP calls, LLM calls, Redis. Without one, a slow dependency makes your requests wait forever, and they pile up until the server dies.

| Call | A sensible start |
| --- | --- |
| Database query | a few seconds |
| Call to another service | 1 to 5 seconds |
| LLM call | 30 to 60 seconds, plus streaming |

## Backpressure

**Backpressure** means "slow down, I am full". A system that cannot say no takes on too much and then collapses.

Ways to push back:

- **Limit concurrency.** A semaphore allows only N tasks at once. Others wait.
- **Bounded queues.** A queue with a maximum size. When full, reject or slow the producer.
- **Load shedding.** Under heavy load, reject some requests early with `503` and keep serving the rest well.
- **Timeouts.** Give up on slow work.

> A fast `503` is better than a slow death. Rejecting some traffic keeps the system alive for the rest.

## Resilience patterns

When your service depends on another one (a payment API, an LLM provider), that other service will sometimes fail.

| Pattern | Idea |
| --- | --- |
| **Retry with backoff and jitter** | try again, waiting longer each time |
| **Circuit breaker** | after many failures, stop calling for a while ("open"), then test with one call ("half-open") |
| **Bulkhead** | separate pools, so one slow dependency cannot use all your resources |
| **Fallback** | a backup: cached data, another provider, a smaller model |

@@ flow | Figure 11.4: circuit breaker states.
Closed|calls go through|green -too many failures-> Open|calls fail fast;no waiting|red -after a pause-> Half-open|let one call test it|yellow
@@ end

The circuit breaker saves you from wasting time on a service that is down, and gives it room to recover.

::: {.box .fastapi}
**How FastAPI does this**

- `async def` routes run on the event loop. Plain `def` routes run in a thread pool, so blocking code is safer there.
- Never call blocking code (`requests`, `time.sleep`, a sync DB driver) inside `async def`. Use `httpx.AsyncClient`, `asyncio.sleep`, and an async driver such as `asyncpg`.
- The pool: `create_async_engine(url, pool_size=10, max_overflow=5, pool_timeout=10)`.
- Limit calls with `asyncio.Semaphore`. Production serving: `gunicorn` with Uvicorn workers.
:::

## Common mistakes

::: {.box .mistake}
**Common mistakes**

- Blocking the event loop with a sync call inside `async def`.
- No timeouts on outgoing calls.
- A pool too big, so all workers together exhaust the database.
- Holding a database session while calling a slow external API.
- Retrying without backoff, which hits a struggling service even harder.
- Using threads for CPU-heavy work in Python and expecting a speed-up.
:::

## Interview corner

::: {.box .interview}
**Interview corner**

**Q: I/O-bound vs CPU-bound? What do you use for each?**
I/O-bound work mostly waits, so use async or threads. CPU-bound work calculates, so use multiple processes (because of the GIL).

**Q: Why use a connection pool?**
Connections are expensive to open and databases allow few. A pool reuses a fixed set of open connections.

**Q: What happens if you block the event loop?**
Every request on that worker freezes, because the single thread is stuck.

**Q: What is backpressure?**
A way for an overloaded part of the system to slow or refuse new work, using limits, bounded queues, timeouts and load shedding.

**Q: Explain a circuit breaker.**
After repeated failures it "opens" and fails calls immediately. After a while it lets one test call through ("half-open"), and closes again if it succeeds.
:::

## Exercises

::: {.box .exercise}
**Exercises**

1. Label each as I/O-bound or CPU-bound and pick a tool: (a) calling an LLM API, (b) resizing 1,000 images, (c) reading 20 database rows.
2. Your app has 8 workers, each with `pool_size=20`. Postgres allows 100 connections. What can happen? What would you change?
3. A coworker writes `time.sleep(5)` inside an `async def` route. Describe exactly what the other users experience.
4. Your payment provider is down. Describe how retry, circuit breaker and fallback work together.
5. **Think:** why is returning `503` quickly sometimes better than trying to serve every request?
:::
