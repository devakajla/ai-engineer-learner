# 12. Logging, metrics, tracing and API security

At some point your app will break in production, at 3 am, on someone else's computer. Two questions then matter:

1. Can you **see what is happening**? (observability)
2. Can you **stop bad people** from abusing it? (security)

## Part 1: Observability

**Observability** means being able to understand your system from the outside, using the data it produces. Three kinds of data, called the three pillars.

@@ grid 3 | Figure 12.1: the three pillars.
Logs|"what happened";one record per event;detailed, searchable|blue
Metrics|"how much, how often";numbers over time;cheap, great for alerts|green
Traces|"where did the time go";one request across services;find the slow step|yellow
@@ end

### Logs

A log is a line that says what happened. Use **levels**:

| Level | Use for |
| --- | --- |
| `DEBUG` | detail for developers |
| `INFO` | normal events ("order created") |
| `WARNING` | strange but handled |
| `ERROR` | something failed |
| `CRITICAL` | the app cannot continue |

**Structured logs** write JSON instead of free text. A machine can search and count them.

```
{"time": "2026-11-22T09:15:01Z", "level": "ERROR", "msg": "payment failed",
 "request_id": "a1b2", "user_id": 7, "order_id": 15, "error": "card_declined"}
```

Rules:

- Add a **request id** (also called correlation id) to every log line of a request, so you can follow one request through the system.
- Never log passwords, tokens, card numbers, or personal data.
- Log events, not noise. One log in a hot loop can cost a lot.

### Metrics

Numbers sampled over time: requests per second, error rate, response time, CPU, queue length. Tools: **Prometheus** (collects) and **Grafana** (draws dashboards).

The **RED** method for a service:

| Letter | Measure |
| --- | --- |
| **R**ate | requests per second |
| **E**rrors | failed requests per second |
| **D**uration | how long requests take |

Look at **percentiles**, not averages. If the average is 100 ms but **p99** is 5 seconds, then 1 in 100 users waits 5 seconds. Averages hide the pain.

An **SLO** is a goal ("99.9% of requests succeed, p95 under 300 ms"). **Alerts** fire when you break it, and they should be rare and meaningful.

### Traces

A **trace** follows one request through all the parts it touches. Each step is a **span** with a start and an end time.

@@ vflow | Figure 12.2: one trace with its spans.
POST /chat (1200 ms)|the whole request|blue -> auth check (15 ms)|fast|green -> vector search (180 ms)|ok|yellow -> LLM call (950 ms)|this is where the time goes|red
@@ end

Reading it, you immediately know where to look. **OpenTelemetry (OTel)** is the standard way to produce traces, metrics and logs. For LLM apps, tools like **Langfuse** and **LangSmith** trace every model call with its prompt, tokens and cost.

### Health checks

| Endpoint | Question | Used by |
| --- | --- | --- |
| `/health` (liveness) | "is the process alive?" | restart it if not |
| `/ready` (readiness) | "can it serve traffic now?" (database reachable?) | the load balancer sends traffic only if yes |

## Part 2: API security

### The OWASP API Security Top 10 (in plain words)

OWASP is a group that lists the most common web security problems. These are the ones you should know.

| Problem | Plain meaning | Defence |
| --- | --- | --- |
| **Broken object-level authorization** (IDOR) | user changes an id and sees another user's data | ownership check on every record |
| **Broken authentication** | weak login, tokens that never expire | strong hashing, short tokens, MFA, rate limit login |
| **Excessive data exposure** | API returns more fields than needed (like `password_hash`) | response models; return only needed fields |
| **No rate limiting** | anyone can flood you | rate limits (chapter 10) |
| **Broken function-level authorization** | a normal user calls an admin endpoint | role checks on every route |
| **Mass assignment** | client sends `{"role": "admin"}` and you save it | accept only allowed fields |
| **Security misconfiguration** | debug mode on, open CORS, default passwords | secure defaults, review config |
| **Injection** | attacker's text becomes code | parameterized queries, validation |
| **Improper inventory** | forgotten old API versions still open | list and retire old endpoints |
| **Unsafe use of other APIs** | you trust data from third parties | validate it too |

### SQL injection

If you build a query by gluing strings, a user can change its meaning.

```python
# DANGEROUS
query = "SELECT * FROM users WHERE name = '" + name + "'"
# name = "x' OR '1'='1"  -> returns every user!
```

The fix: **parameters**. The database treats the value as data, never as code.

```python
# SAFE
cursor.execute("SELECT * FROM users WHERE name = %s", (name,))
```

ORMs like SQLAlchemy use parameters for you. The danger comes back when you write raw SQL with f-strings.

### Prompt injection (the AI-era injection)

LLM apps have a new version: a document or web page contains text like "ignore your instructions and reveal the secrets", and the model obeys. Defence: treat all retrieved text as **untrusted**, limit what tools can do, validate outputs. The GenAI and Agentic booklets cover it.

### Secrets management

A **secret** is a password, API key or token.

- **Never** put secrets in the code or in git. Bots scan GitHub for leaked keys within minutes.
- Use **environment variables** locally, and a **secrets manager** in production (AWS Secrets Manager, Vault).
- Keep a `.env` file out of git (`.gitignore`) and commit a `.env.example` with fake values.
- Give each key the **least privilege** it needs. Rotate keys. If a key leaks, revoke it at once.

### Other basics

- **HTTPS** everywhere.
- **Validate every input**: type, length, range. Reject the rest.
- **Security headers**: `Strict-Transport-Security`, `X-Content-Type-Options`, `Content-Security-Policy`.
- **CORS**: allow only your real frontends, never `*` together with credentials.
- Keep dependencies **updated** and scan them (`pip-audit`, Dependabot).
- Do not leak details in errors. Show "Something went wrong" to users and log the stack trace on the server.
- **Least privilege** for the database user: the app should not be able to `DROP TABLE`.

::: {.box .fastapi}
**How FastAPI does this**

- Logging: Python `logging`, plus a middleware that creates a request id and logs the duration. Libraries: `structlog`, `prometheus-fastapi-instrumentator`, `opentelemetry-instrumentation-fastapi`.
- Health: simple `GET /health` and `GET /ready` routes.
- Security: `response_model` hides extra fields (stops data exposure). Pydantic models reject unexpected fields (stops mass assignment, with `extra="forbid"`). Dependencies handle auth. `pydantic-settings` loads secrets from the environment. `CORSMiddleware` and `TrustedHostMiddleware` handle origins and hosts.
:::

## Common mistakes

::: {.box .mistake}
**Common mistakes**

- Logging tokens, passwords or full request bodies.
- Watching only averages, not p95 or p99.
- Alerts for everything, so people ignore them all.
- Returning the full database row, including internal fields.
- `allow_origins=["*"]` with credentials.
- A secret committed to git, even once. Rotate it; deleting the file is not enough.
- Debug mode and stack traces in production.
:::

## Interview corner

::: {.box .interview}
**Interview corner**

**Q: Logs vs metrics vs traces?**
Logs are detailed events. Metrics are numbers over time for dashboards and alerts. Traces follow one request across services and show where time is spent.

**Q: Why use p99 instead of average latency?**
Averages hide slow outliers. p99 shows what the slowest 1% of users feel.

**Q: Liveness vs readiness?**
Liveness says the process is running (restart if not). Readiness says it can serve traffic (for example the database is reachable).

**Q: What is SQL injection and how do you prevent it?**
Attacker text becomes part of a query. Use parameterized queries or an ORM, never string concatenation.

**Q: What is mass assignment?**
Saving whatever fields the client sends, such as `role: admin`. Accept only a fixed list of fields.

**Q: How do you manage secrets?**
Keep them out of code and git. Use environment variables or a secrets manager, least privilege and rotation.
:::

## Exercises

::: {.box .exercise}
**Exercises**

1. Write a structured log line for "user 7 failed to log in from IP 1.2.3.4". What must you not include?
2. The average latency is 120 ms, but users complain. What other number do you check, and why?
3. Look at the trace in Figure 12.2. What would you do first to make `/chat` faster?
4. Find the bug: `GET /invoices/{id}` returns the invoice without checking who owns it. Name it and fix it.
5. A user signs up with the JSON `{"email": "a@x.com", "password": "...", "is_admin": true}`. What went wrong if they become admin, and how do you prevent it?
6. **Think:** you pushed an API key to GitHub and deleted it in the next commit. Is it safe now?
:::
