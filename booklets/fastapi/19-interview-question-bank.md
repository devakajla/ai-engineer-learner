# 19. Interview question bank

Short answers you can say out loud. Read a question, answer it yourself first, then compare. For the **why**, go back to the chapter named in brackets.

## A. FastAPI basics

**1. What is FastAPI and why use it?** A modern Python web framework built on Starlette (web) and Pydantic (validation). It gives type-based validation, automatic docs, async support and good speed. [2, 4]

**2. How does FastAPI create `/docs`?** From your type hints and Pydantic models it builds an OpenAPI schema, and Swagger UI shows it at `/docs` (ReDoc at `/redoc`). [2]

**3. Path, query and body parameters: how does FastAPI tell them apart?** A name in the path is a path parameter. A simple type not in the path is a query parameter. A Pydantic model is the body. [3, 4]

**4. What is `response_model` for?** It filters and validates the output, so fields like `password_hash` never leak, and it documents the response shape. [5]

**5. PUT vs PATCH?** PUT replaces the whole resource. PATCH changes only the sent fields (`model_dump(exclude_unset=True)`). [4]

**6. How do you return a custom status code?** `status_code=` in the decorator, or `HTTPException(status_code=...)` for errors. [5]

**7. What is a `422` error?** Validation failed. The body says which field (`loc`) and why (`msg`). [3, 4]

**8. How do you handle custom errors globally?** Raise your own exception classes in services and register `@app.exception_handler(...)` to convert them to JSON responses. [5, 10]

## B. Pydantic and validation

**9. What does Pydantic do?** Checks and converts data against type hints and rules, and gives clear errors.

**10. `Field` vs `field_validator`?** `Field` is for simple rules (min, max, pattern). `field_validator` is for custom logic. [4]

**11. Why separate `TaskCreate`, `TaskUpdate` and `TaskOut`?** Input and output differ: the client must not set `id` or read secrets, and updates are partial. [4, 5]

**12. What does `from_attributes=True` do?** Lets a Pydantic model read values from object attributes, such as an ORM row. [8]

## C. Structure and dependency injection

**13. How do you structure a FastAPI project?** Routes, services, repositories, schemas, core and db, with imports going downward only. [6]

**14. What is dependency injection in FastAPI?** A route declares what it needs with `Depends`, and FastAPI builds and passes it in. [7]

**15. Why is `Depends` good for testing?** You can replace any dependency with `app.dependency_overrides`. [7, 15]

**16. What is a `yield` dependency?** One that sets something up before the route and cleans up after it (a database session). [7, 8]

**17. Why `pydantic-settings`?** Typed settings read from environment variables and `.env`, validated at startup. [6]

**18. What is the application factory pattern?** A `create_app()` function that builds the app, so tests and different environments can create fresh instances. [6]

## D. Async

**19. `def` vs `async def` routes?** `async def` runs on the event loop and must never block. `def` runs in a thread pool, so blocking code is safe. [9]

**20. What happens with `time.sleep` in an `async def` route?** The event loop blocks, and every other request waits. Three parallel 2 s requests took 6 s instead of 2 s in our test. [9]

**21. When does async help?** When work is mostly **waiting** (database, network). It does not speed up CPU work. [9]

**22. What is `asyncio.gather`?** Runs several awaitables concurrently and returns all results. [9]

**23. How do you limit concurrent calls?** `asyncio.Semaphore`. [9, 17]

## E. Database

**24. What is SQLAlchemy's engine vs session?** The engine holds the connection pool (one per app). A session is a unit of work (one per request). [8]

**25. Why Alembic?** Versioned, repeatable schema changes for every environment. [8]

**26. What is the N+1 problem and the fix?** One query for a list plus one per item. Fix with `selectinload` or `joinedload`, or a join. [8, Backend 4]

**27. Why `expire_on_commit=False` with async?** After commit, objects would expire and a later attribute access would try to load lazily, which fails in async code. [8]

**28. How do you avoid SQL injection?** Use the ORM or bound parameters, never build SQL by joining user text. [8]

## F. Auth and security

**29. Explain the JWT login flow.** Check the password, return a signed token with `sub` and `exp`. The client sends `Authorization: Bearer <token>`, a dependency verifies it and loads the user. [11]

**30. How do you store passwords?** A slow salted hash (Argon2 or bcrypt). [11]

**31. Authentication vs authorization?** Who are you, versus what may you do. [11]

**32. What is IDOR and how do you prevent it?** Accessing another user's data by guessing an id. Check ownership in the service on every access. [11]

**33. Why the same error for "no user" and "wrong password"?** To not reveal which emails exist. [11]

**34. What does CORS do?** Tells browsers which other origins may call your API. It does not protect your API from scripts. [10]

**35. Name some security basics for an API.** Hash passwords, strong secret in env, HTTPS, validate input and sizes, rate limit, ownership checks, no stack traces to clients, safe file uploads, dependency updates. [10, 11, 14]

## G. Background work and streaming

**36. `BackgroundTasks` vs a queue?** `BackgroundTasks` runs in the web process after the response and is lost on restart. A queue with workers is durable, retryable and scalable. [12]

**37. What status for starting a long job?** `202 Accepted` with a job id and a status endpoint. [12]

**38. Why idempotent jobs?** Delivery is at-least-once, so a job may run twice. [12]

**39. SSE vs WebSocket?** SSE is one-way over HTTP and reconnects by itself. WebSocket is two-way. Use SSE for LLM token streams. [13]

**40. How do you stream an LLM answer?** Call with `stream=True`, loop over chunks in an async generator and return it via `EventSourceResponse` or `StreamingResponse`. [13, 17]

**41. How do you scale WebSockets?** Share messages through Redis pub/sub because connections live in one process. [13]

## H. Files, cookies, middleware

**42. How do you handle uploads safely?** Limit size, check type, sanitise the name, store outside code (object storage in production). [14]

**43. What is middleware and when do you use it?** Code around every request: logging, request id, CORS, compression. [10]

**44. What is `lifespan`?** Startup and shutdown code in one function. [10]

**45. Cookie flags?** `HttpOnly`, `Secure`, `SameSite`, plus `max_age`. [14]

## I. Testing, deployment, LLM

**46. How do you test a FastAPI app?** `AsyncClient` with `ASGITransport`, a fresh in-memory database per test, dependency overrides, fakes for outside services. [15]

**47. Liveness vs readiness?** Alive versus able to serve (database reachable). [16]

**48. Why order Dockerfile steps this way?** Dependencies first for layer caching. [16]

**49. How many uvicorn workers?** About one per CPU core, or one per container when an orchestrator scales containers. [16]

**50. How do you make LLM calls reliable?** Timeout, token cap, retries with backoff for temporary errors, fallback model, structured output validation. [17]

**51. How do you control LLM cost?** Token caps, per-user limits and budgets, caching, cheaper models for easy tasks, usage logging. [17]

**52. What is prompt injection?** Text that tries to override your instructions. Separate system and user content, limit capabilities, validate output. [17]

## Coding questions to practise on paper

1. Write a route `GET /items/{id}` that returns `404` with a JSON error shape if the item is missing.
2. Write a dependency that checks the header `X-API-Key` and returns `401` if wrong.
3. Write a Pydantic model for a signup with email, password (min 8) and age (18 to 120).
4. Write an async function that fetches three URLs together with a timeout of 5 seconds.
5. Write a pytest test for a route that needs login.
6. Write a middleware that adds `X-Process-Time`.

*Sample answers for 1 to 3 are in the answers chapter.*
