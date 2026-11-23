# 12. Background tasks and queues

Some jobs are slow: sending an email, making a report, calling an LLM, processing a file. If the route does them, the user waits and your server is busy.

The pattern: **answer fast, work later.** (The Backend booklet, chapter 9, explains why. Here we build it.)

You have two tools:

| Tool | Where it runs | Survives a restart? | Use it for |
| --- | --- | --- | --- |
| `BackgroundTasks` | in the same server process, after the response | no | tiny, non-critical jobs |
| A queue + a worker (ARQ) | in a separate process | yes | important or slow jobs |

## Part 1: `BackgroundTasks`

FastAPI can run a function **after** it sends the response. The client does not wait.

In `app/api/routes/tasks.py`:

```python
import logging

from fastapi import BackgroundTasks

logger = logging.getLogger(__name__)


def log_task_created(task_id: int) -> None:
    logger.info("task created id=%s", task_id)


@router.post("", response_model=TaskOut, status_code=status.HTTP_201_CREATED)
async def create_task(
    data: TaskCreate, user: CurrentUser, service: TaskServiceDep, background: BackgroundTasks
):
    task = await service.create_task(user.id, data)
    background.add_task(log_task_created, task.id)   # runs after the response is sent
    return task
```

`background.add_task(function, arg1, arg2)` schedules the call. The response goes out first.

Good for: writing an audit log, sending a non-critical notification.

Not good for: anything that **must not be lost** (a payment receipt) or that takes a long time (it uses your web server's resources). If the server restarts, the task is gone.

## Part 2: a real queue with ARQ

**ARQ** is a small async job queue that uses **Redis** as the broker. It fits FastAPI well because jobs are `async` functions too.

@@ flow | Figure 12.1: three processes work together.
FastAPI|enqueues a job;returns 202 fast|blue -job-> Redis|holds the queue|red -job-> Worker (ARQ)|runs the job;saves the result|green
@@ end

::: {.step}
Step 1: run Redis and install ARQ
:::

```bash
docker run -d --name redis -p 6379:6379 redis:7
uv add arq
```

(If you do not have Docker yet, chapter 16 shows it. You can also install Redis with `brew install redis` and run `redis-server`.)

Add to `Settings`: `redis_url: str = "redis://localhost:6379"`.

::: {.step}
Step 2: write a job and the worker settings
:::

Create `app/worker.py`:

```python
import asyncio
import logging

from arq.connections import RedisSettings
from arq.worker import Retry

logger = logging.getLogger("worker")


async def make_report(ctx: dict, user_id: int) -> dict:
    """A slow job. `ctx` is a dictionary ARQ passes to every job."""
    logger.info("making report for user %s (try %s)", user_id, ctx["job_try"])
    await asyncio.sleep(5)                      # pretend this takes a while
    return {"user_id": user_id, "tasks_done": 12}


async def flaky_job(ctx: dict, url: str) -> str:
    try:
        return await call_some_api(url)         # may fail sometimes
    except ConnectionError:
        # try again later: wait 5s, then 10s, then 15s...
        raise Retry(defer=ctx["job_try"] * 5)


class WorkerSettings:
    functions = [make_report, flaky_job]
    redis_settings = RedisSettings()            # localhost:6379
    max_tries = 5                               # give up after 5 tries
```

- A job is an `async def` whose first argument is `ctx`.
- `max_tries` is the retry limit. Raising `Retry(defer=seconds)` asks ARQ to run the job again later. This is **backoff**: wait longer each time.
- Start the worker in its **own terminal**, separate from the web server:

```bash
uv run arq app.worker.WorkerSettings
# -> Starting worker for 2 functions: make_report, flaky_job
```

::: {.step}
Step 3: enqueue from the route
:::

Open one Redis pool when the app starts, and close it at the end. This is the `lifespan` (chapter 10) at work:

```python
from arq import create_pool
from arq.connections import RedisSettings

@asynccontextmanager
async def lifespan(app: FastAPI):
    setup_logging()
    app.state.arq = await create_pool(RedisSettings.from_dsn(get_settings().redis_url))
    yield
    await app.state.arq.close()
```

A route that starts a job and returns `202`:

```python
from fastapi import Request
from arq.jobs import Job

router = APIRouter(prefix="/reports", tags=["reports"])


@router.post("", status_code=status.HTTP_202_ACCEPTED)
async def start_report(request: Request, user: CurrentUser):
    job = await request.app.state.arq.enqueue_job("make_report", user.id)
    return {"job_id": job.job_id, "status": "queued"}


@router.get("/{job_id}")
async def report_status(job_id: str, request: Request, user: CurrentUser):
    job = Job(job_id, request.app.state.arq)
    status_ = await job.status()
    if status_.value == "complete":
        return {"status": "done", "result": await job.result()}
    return {"status": status_.value}
```

Try it:

```bash
curl -X POST localhost:8000/api/v1/reports -H "Authorization: Bearer $TOKEN"
# -> {"job_id":"4c1f...","status":"queued"}           (instant)
curl localhost:8000/api/v1/reports/4c1f... -H "Authorization: Bearer $TOKEN"
# -> {"status":"in_progress"}                         (a few seconds later:)
# -> {"status":"done","result":{"user_id":1,"tasks_done":12}}
```

The user is never kept waiting. The job states are `queued`, `in_progress`, `complete`, `deferred` and `not_found`.

## The rules of good jobs

@@ grid 3 | Figure 12.2: how to write jobs that survive real life.
Idempotent|running it twice gives the same result as once;(queues may deliver twice)|green
Small data|pass ids, not big objects;load data inside the job|blue
Retry smartly|backoff, a max number of tries;a dead-letter place for failures|yellow
@@ end

**Idempotency with ARQ:** give the job your own id. If a job with that id already exists, `enqueue_job` returns `None` instead of creating a second one:

```python
job = await pool.enqueue_job("make_report", user.id, _job_id=f"report:{user.id}:2026-11")
if job is None:
    ...  # a report job for this user and month already exists
```

## Which one should I use?

| Question | `BackgroundTasks` | ARQ or Celery |
| --- | --- | --- |
| Is losing the job a problem? | yes, use a queue | fine |
| Does it take more than a second or two? | yes, use a queue | fine |
| Need retries or a status? | yes, use a queue | yes |
| Need to scale workers separately? | yes, use a queue | yes |

**Celery** is the older, bigger tool with more features (but synchronous by default). ARQ is smaller and async. The ideas are identical.

::: {.box .checkpoint}
**Folder now**

```
app/
├── worker.py                # NEW: job functions + WorkerSettings
├── main.py                  # lifespan opens and closes the Redis pool
└── api/routes/reports.py    # NEW: start a report, check its status
```

**Checkpoint:** creating a task logs `task created id=...` after the response (`BackgroundTasks`). With Redis and the worker running, `POST /reports` returns a `job_id` at once, and the status becomes `done` a few seconds later.
:::

## Common mistakes

::: {.box .mistake}
**Common mistakes**

- Using `BackgroundTasks` for work that must not be lost.
- Starting the worker but forgetting Redis, or the other way round.
- Jobs that are not idempotent, so a retry does the action twice.
- Putting a whole big object in the job arguments. Pass an id.
- Retrying instantly with no wait.
- Running the worker with different settings or code than the API.
:::

## Interview corner

::: {.box .interview}
**Interview corner**

**Q: `BackgroundTasks` vs Celery or ARQ?**
`BackgroundTasks` runs in the web process after the response and is lost on a restart. A queue with workers survives restarts, can retry, scale separately and report status.

**Q: What should a route return when it starts a long job?**
`202 Accepted` with a job id and a way to check its status.

**Q: Why must jobs be idempotent?**
Queues give at-least-once delivery, so a job may run twice.

**Q: How do you retry a failing job well?**
A limited number of tries, with growing waits (backoff) and jitter, then a dead-letter queue for the failures.
:::

## Exercises

::: {.box .exercise}
**Exercises**

1. Add a background task that logs `"welcome email to <email>"` after a user registers.
2. Make `make_report` fail on the first try (raise `Retry`) and watch the worker log `(try 2)`.
3. Use `_job_id` to stop a user from starting two reports in the same minute.
4. Write the job `summarize_task(ctx, task_id)` that loads the task by id and logs its title (use a new database session inside the job).
5. **Think:** which of these must use a real queue: writing a log, sending a payment receipt, resizing an image? Why?
:::
