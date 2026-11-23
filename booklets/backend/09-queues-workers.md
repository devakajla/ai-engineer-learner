# 9. Queues and workers

Some work is slow: sending an email, making a PDF, calling an LLM, processing a big file. If your API does it **inside** the request, the user stares at a spinner, and your server is busy.

A better way: accept the request, put a **job** in a **queue**, answer immediately, and let a separate **worker** do the job in the background.

Real life: in a restaurant, the waiter does not cook. He writes the order on a slip and puts it on the kitchen rail. The cooks pick slips one by one. The waiter is free to serve the next table.

## The picture

@@ flow | Figure 9.1: producer, broker, worker.
API (producer)|creates a job;answers fast|blue -push-> Queue (broker)|holds jobs;in order|yellow -pull-> Worker|does the slow work|green -save-> Database|stores the result|purple
@@ end

- **Producer**: the code that creates jobs (your API).
- **Broker**: the queue that holds them (Redis, RabbitMQ, Kafka, or a cloud queue like SQS).
- **Worker**: a separate process that takes jobs and runs them. You can run many workers.

## What the user sees: 202 Accepted

```
POST /reports        -> 202 Accepted   {"job_id": "abc123"}
GET  /reports/abc123 -> 200 OK         {"status": "running"}
GET  /reports/abc123 -> 200 OK         {"status": "done", "url": "/files/r.pdf"}
```

`202` means "I accepted it, it is not done yet". The client **polls** the status URL, or you **push** the result with a webhook or a WebSocket.

A job goes through states:

@@ flow | Figure 9.2: the life of a job.
queued|waiting|gray -> running|a worker took it|blue -> succeeded|result saved|green
@@ end

A job can also end in `failed`, which leads to a retry (below).

## Why queues help

| Benefit | Meaning |
| --- | --- |
| Fast responses | the user does not wait |
| Smoothing | a burst of 10,000 requests becomes a line, not a crash |
| Isolation | a crashing job does not crash the API |
| Scale | add more workers when the queue grows |
| Retries | failed jobs can run again |

## Retries and backoff

Jobs fail: a network blip, a rate limit, a busy service. Retry them, but wisely.

- **Backoff**: wait longer after each failure (1 s, 2 s, 4 s, 8 s). Hammering a struggling service makes it worse.
- **Jitter**: add randomness so a thousand workers do not retry at the same moment.
- **Max attempts**: stop after, say, 5 tries.

After the last attempt, move the job to a **dead-letter queue (DLQ)**: a parking place for jobs that kept failing. A human can look at them later. Never silently drop them.

## Idempotent jobs: the golden rule

Most queues give **at-least-once** delivery: a job will run at least once, but *maybe twice* (for example, a worker crashes after finishing but before telling the broker). So the job must be **safe to run twice**.

| Delivery | Meaning |
| --- | --- |
| At-most-once | maybe lost, never twice |
| **At-least-once** | never lost, maybe twice (the usual one) |
| Exactly-once | very hard; usually faked with idempotency |

How to make a job idempotent:

- Give the job a unique id and record "done" for it. If it is done, skip.
- Use operations that are naturally repeatable: "set status = paid", not "add 100 to balance".
- Use a `UNIQUE` key in the database for the result.

## Queue vs pub/sub

| | Queue | Pub/Sub |
| --- | --- | --- |
| Who gets a message | **one** worker | **every** subscriber |
| Use | share the work | broadcast an event |
| Example | resize this image | "order paid", tell billing, email and analytics |

## Which broker?

| Tool | Style | Pick it when |
| --- | --- | --- |
| **Redis** (with ARQ, RQ, Celery) | simple lists | small and medium apps, you already have Redis |
| **RabbitMQ** | smart routing, acknowledgements | complex routing, reliable task queues |
| **Kafka** | a durable, replayable log | very high volume event streams; many consumers; replay history |
| **SQS** (AWS) | managed queue | you are on AWS and want no servers to run |

Kafka is a log, not a classic queue. Messages stay after being read, and consumers keep an "offset" (their position). That allows replay.

## Task libraries in Python

| Library | Notes |
| --- | --- |
| **Celery** | the classic, many features, sync workers |
| **ARQ** | small, **async**, Redis only, a good fit for FastAPI |
| **RQ** | very simple, Redis |
| `BackgroundTasks` (FastAPI) | runs after the response, **in the same process** |

`BackgroundTasks` is fine for tiny, non-critical work (a log line). If the server restarts, the task is lost. For anything important or slow, use a real queue.

## Scheduled jobs

Some jobs run on a clock: "every night at 2 am, clean old data". Use **cron**, Celery beat or a scheduler service. Make them idempotent too, because a restart may run them twice.

## Why this matters for LLM apps

An LLM call can take 5 to 30 seconds. Document ingestion (parse, chunk, embed, index) takes minutes. Both belong in a queue. The API returns `202` and the worker does the heavy work.

::: {.box .fastapi}
**How FastAPI does this**

- Tiny jobs: `BackgroundTasks` and `background_tasks.add_task(send_email, user)`.
- Real jobs: an **ARQ** or **Celery** worker is a separate process with the same codebase. The route enqueues, for example `await arq_pool.enqueue_job("make_report", user_id)`, and returns `202` with the job id.
- A status route reads the job state from Redis or your database.
:::

## Common mistakes

::: {.box .mistake}
**Common mistakes**

- Doing a long job inside the request.
- Using `BackgroundTasks` for work that must not be lost.
- Jobs that are not idempotent, so a retry charges the customer twice.
- Retrying instantly with no backoff.
- No dead-letter queue, so failures vanish.
- Putting big files in the queue message. Put an id or a link, not the data.
:::

## Interview corner

::: {.box .interview}
**Interview corner**

**Q: Why use a queue?**
To keep requests fast, smooth traffic spikes, isolate failures, scale workers, and retry failed work.

**Q: What does at-least-once delivery mean for your code?**
A job may run more than once, so it must be idempotent.

**Q: What is a dead-letter queue?**
A queue for jobs that failed all retries, kept for a human to inspect.

**Q: Queue vs pub/sub?**
A queue gives each message to one worker. Pub/sub gives each message to all subscribers.

**Q: RabbitMQ vs Kafka?**
RabbitMQ is a smart broker for task queues with routing and acknowledgements. Kafka is a durable log for huge event streams, where consumers track their offset and can replay.

**Q: `BackgroundTasks` vs Celery?**
`BackgroundTasks` runs in the web process after the response and is lost on a crash. Celery or ARQ use a broker and separate workers, so jobs survive restarts and can be retried.
:::

## Exercises

::: {.box .exercise}
**Exercises**

1. A user uploads a 200 page PDF to be summarised by an LLM. Design the flow with a queue: what does the API return, what does the worker do, and how does the user get the result?
2. A job "send welcome email" can run twice. How do you make sure the user gets only one email?
3. Write a retry plan for a job that calls an API that sometimes returns `429`: attempts, waits and the final step.
4. Choose queue or pub/sub: (a) resize images, (b) tell three services that an order was paid.
5. Why is "add 100 to balance" a bad job, and what is a safer version?
6. **Think:** your queue grows to 50,000 waiting jobs. List two things you could do.
:::
