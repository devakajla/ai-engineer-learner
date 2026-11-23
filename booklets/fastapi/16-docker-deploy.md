# 16. Docker and deployment

"It works on my machine" is the oldest problem in software. **Docker** solves it: you pack your app, Python and all libraries into one **image**. That image runs the same on your laptop, a teammate's laptop and a server.

> Docker was not available on the machine where this booklet was written, so the commands in this chapter follow the standard, well-known Docker form but were **not run here**. Run each one yourself. If something differs, the error message will tell you. The Python side (settings, health checks) was tested.

## Idea: image and container

| Word | Meaning | Like |
| --- | --- | --- |
| **Image** | a packed, read-only recipe result: OS pieces, Python, your code | a class |
| **Container** | a running copy of an image | an object |
| **Dockerfile** | the text recipe to build an image | the class code |
| **Compose** | one file that runs several containers together | a launcher |

@@ flow | Figure 16.1: from code to a running container.
Dockerfile|the recipe|blue -docker build-> Image|packed app|yellow -docker run-> Container|running app|green
@@ end

## Steps

::: {.step}
Step 1: a health route that checks the database
:::

Deployers and orchestrators ask your app "are you alive?" and "are you ready?". These are two different questions.

| Check | Question | Fails when | Used to |
| --- | --- | --- | --- |
| **Liveness** `/health` | is the process running? | the app is stuck | restart it |
| **Readiness** `/ready` | can it serve traffic now? | the database is down | stop sending traffic |

Add to `app/api/routes/health.py`:

```python
from fastapi import APIRouter, HTTPException
from sqlalchemy import text

from app.api.deps import SessionDep

router = APIRouter(tags=["health"])


@router.get("/health")
async def health():
    return {"status": "ok"}


@router.get("/ready")
async def ready(session: SessionDep):
    try:
        await session.execute(text("SELECT 1"))
    except Exception:
        raise HTTPException(503, "database not ready")
    return {"status": "ready"}
```

`503 Service Unavailable` tells the platform "do not send me requests yet".

::: {.step}
Step 2: the Dockerfile
:::

Create `Dockerfile` in the project root:

```dockerfile
FROM python:3.12-slim

# install uv (a fast package manager)
COPY --from=ghcr.io/astral-sh/uv:latest /uv /bin/uv

WORKDIR /code

# 1) copy only the dependency files first, and install
COPY pyproject.toml uv.lock ./
RUN uv sync --frozen --no-dev --no-install-project

# 2) then copy the code
COPY app ./app
COPY alembic ./alembic
COPY alembic.ini ./

# run as a normal user, not root
RUN useradd --create-home appuser
USER appuser

EXPOSE 8000
CMD ["uv", "run", "--no-dev", "uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
```

Why each part:

- `python:3.12-slim` is a small base image. Smaller means faster and fewer security holes.
- **Layer caching.** Docker caches each step. Dependencies change rarely, code changes often. By copying `pyproject.toml` and `uv.lock` **first**, the slow "install" step is reused when only your code changed.
- `--frozen` installs exactly the versions in `uv.lock`. `--no-dev` skips test tools.
- `USER appuser`: if someone breaks in, they are not root.
- `--host 0.0.0.0` makes the app reachable from outside the container. (`127.0.0.1` would only be reachable inside it.)

Add a `.dockerignore` file so junk is not copied in:

```
.venv
__pycache__
.git
.env
*.db
tests
uploads
```

Never copy `.env` into an image. Pass settings when you **run** the container.

Build and run:

```bash
docker build -t taskflow .
docker run --rm -p 8000:8000 -e SECRET_KEY=$(openssl rand -hex 32) taskflow
# open http://localhost:8000/health
```

`-p 8000:8000` connects your port 8000 to the container's. `-e` passes an environment variable.

::: {.step}
Step 3: Postgres and friends with Compose
:::

A real app needs a database (and Redis for the queue). `docker-compose.yml`:

```yaml
services:
  db:
    image: postgres:16
    environment:
      POSTGRES_USER: taskflow
      POSTGRES_PASSWORD: taskflow
      POSTGRES_DB: taskflow
    volumes:
      - pgdata:/var/lib/postgresql/data
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U taskflow"]
      interval: 5s
      retries: 10

  redis:
    image: redis:7

  api:
    build: .
    ports:
      - "8000:8000"
    environment:
      DATABASE_URL: postgresql+asyncpg://taskflow:taskflow@db:5432/taskflow
      REDIS_URL: redis://redis:6379
      SECRET_KEY: ${SECRET_KEY}
    depends_on:
      db:
        condition: service_healthy
      redis:
        condition: service_started
    command: >
      sh -c "uv run --no-dev alembic upgrade head &&
             uv run --no-dev uvicorn app.main:app --host 0.0.0.0 --port 8000"

  worker:
    build: .
    environment:
      DATABASE_URL: postgresql+asyncpg://taskflow:taskflow@db:5432/taskflow
      REDIS_URL: redis://redis:6379
      SECRET_KEY: ${SECRET_KEY}
    depends_on:
      - redis
    command: uv run --no-dev arq app.worker.WorkerSettings

volumes:
  pgdata:
```

Things to notice:

- Containers reach each other **by service name**: the database host is `db`, not `localhost`.
- The database URL changes only in the environment. The code is the same. This is the payoff of chapter 6.
- `volumes: pgdata` keeps database files when the container is replaced.
- `depends_on` with a **health check** waits until Postgres is really ready.
- The `api` runs the migration first (`alembic upgrade head`), then starts the server.
- The **worker** uses the same image with a different command.
- You need the Postgres driver: `uv add asyncpg`.

```bash
export SECRET_KEY=$(openssl rand -hex 32)
docker compose up --build
docker compose logs -f api
docker compose down          # stop (data stays); add -v to delete the data too
```

@@ grid 2 | Figure 16.2: what Compose starts.
db|Postgres 16;volume pgdata|purple
redis|queue broker|red
api|FastAPI on port 8000;runs migrations first|green
worker|ARQ, the same image;different command|blue
@@ end

::: {.step}
Step 4: run it for real: workers
:::

`fastapi dev` is for development only (it reloads on every change). In production you run `uvicorn` (or `fastapi run`), often with several worker processes:

```bash
uv run uvicorn app.main:app --host 0.0.0.0 --port 8000 --workers 4
```

Each worker is a separate process with its own event loop. Four workers use four CPU cores. A common starting point: workers = number of CPU cores. In Kubernetes you usually run **one** worker per container and add more containers instead.

Because there are several processes, **memory is not shared**: an in-memory list, an in-memory cache, or a WebSocket list lives in one worker only. That is why we moved to a database and Redis.

Put a **reverse proxy** (Nginx, Caddy, or a cloud load balancer) in front. It handles HTTPS, buffering, and sends traffic to your workers. If your app is behind a proxy, add `--proxy-headers` so it sees the real client address.

**Graceful shutdown:** when a container is stopped, uvicorn finishes the requests in progress and then exits (our `lifespan` code after `yield` runs then). Give it time: `docker stop -t 30`.

::: {.step}
Step 5: CI with GitHub Actions
:::

Create `.github/workflows/ci.yml`. On every push, install, test and build:

```yaml
name: CI
on: [push, pull_request]

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: astral-sh/setup-uv@v5
      - run: uv sync
      - run: uv run pytest -q

  build:
    needs: test
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - run: docker build -t taskflow .
```

`needs: test` means the image is built only if tests pass. Action versions change; check the Marketplace for the newest.

## Settings and secrets in production

@@ vflow | Figure 16.3: where each kind of setting lives.
Code (git)|defaults that are safe: app name, token minutes|green -overridden by-> Environment variables|per environment: DATABASE_URL, REDIS_URL, CORS_ORIGINS|yellow -overridden by-> Secret store|SECRET_KEY, API keys: from the platform's secrets, never in git|red
@@ end

Rules:

- Never commit `.env`. Commit `.env.example` with fake values.
- Use a different `SECRET_KEY` for each environment.
- Do not log secrets.
- `CORS_ORIGINS` in production lists your real site only.
- Turn off docs if the API is private (`FastAPI(docs_url=None, redoc_url=None)`).

## A deploy checklist

1. Tests pass in CI.
2. The image builds and runs as a non-root user.
3. Settings come from the environment.
4. Migrations run **before** the new code takes traffic.
5. `/health` and `/ready` work.
6. Logs go to stdout (the platform collects them).
7. There is a way to roll back to the last image.

::: {.box .checkpoint}
**Folder now**

```
taskflow/
├── Dockerfile
├── .dockerignore
├── docker-compose.yml
├── .env.example
├── .github/workflows/ci.yml
└── app/ ...
```

**Checkpoint:** `docker compose up --build` starts four services, and `curl localhost:8000/ready` returns `{"status":"ready"}`.
:::

## Common mistakes

::: {.box .mistake}
**Common mistakes**

- Copying the code before installing dependencies, so every build reinstalls everything.
- Baking secrets (`.env`) into the image.
- Running as root.
- `localhost` as the database host inside Compose. Use the service name.
- Using `fastapi dev` (auto reload) in production.
- No health checks, so the platform cannot tell when the app is broken.
- Running migrations by hand and forgetting.
- Storing data inside a container without a volume. It disappears with the container.
:::

## Interview corner

::: {.box .interview}
**Interview corner**

**Q: Image vs container?**
An image is the packed read-only template. A container is a running instance of it.

**Q: Why copy dependency files before the code in a Dockerfile?**
Layer caching: the slow install layer is reused unless the dependencies changed.

**Q: Liveness vs readiness?**
Liveness says the process is alive (restart if not). Readiness says it can serve traffic, for example the database is reachable (stop routing if not).

**Q: How many uvicorn workers?**
About one per CPU core on a plain server, or one per container with the orchestrator scaling containers.

**Q: How do you manage secrets?**
Environment variables injected from a secret manager. Never in git or in the image.

**Q: What is a graceful shutdown?**
Stop taking new requests, finish the current ones, close connections, then exit.
:::

## Exercises

::: {.box .exercise}
**Exercises**

1. Write the Dockerfile and build it. Check the size with `docker images`. Then change one line of code and rebuild. Which layers were cached?
2. Add `/ready` and stop the `db` container. What does `/ready` return?
3. Add a second `api` replica in Compose. What breaks if your app keeps state in memory?
4. Write `.env.example` with every setting, using fake values.
5. Extend the CI file with a lint step (`uv run ruff check`).
6. **Think:** why does the migration run before the new version starts and not after?
:::
