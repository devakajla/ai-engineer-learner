---
title: Level 1 interview questions
summary: Common interview questions on HTTP, REST, FastAPI basics, Pydantic, errors and project structure, with short answers and follow-ups.
plan_ids: [BE-01, FA-01, FA-08, SD-01]
---

This lesson is practice for interviews. Use it like this:

1. Read a question and **answer it out loud first**. (Or type your answer to Claude in the side panel: *"Grade my answer like a senior backend interviewer"*.)
2. Then read the model answer.
3. Try the **follow-up** questions. Interviews are often won on the follow-ups.

If an answer feels unclear, go back to the lesson it comes from. Each section says which one.

## 1. HTTP and REST (lesson 1)

**Q: A client sends `POST /orders` and the connection drops before the answer arrives. What can go wrong, and how do you make a retry safe?**

**A:** The client does not know if the order was created. If it just sends the request again, the order may be created twice, because `POST` is not idempotent. The fix is an **idempotency key**. The client sends a header `Idempotency-Key` with a unique value. The server saves the key together with the result. If the same key comes again, the server returns the saved result and does not create a new order.

- *Follow-up: Which methods are safe? Which are idempotent?* Safe (no change to data): `GET`, `HEAD`, `OPTIONS`. Idempotent (repeating gives the same state): `GET`, `PUT`, `DELETE`, `HEAD`, `OPTIONS`. `POST` and `PATCH` are not guaranteed to be.
- *Follow-up: PUT vs PATCH?* `PUT` replaces the whole thing. `PATCH` changes only the fields that were sent.
- *Follow-up: 401 vs 403?* `401`: not logged in ("who are you?"). `403`: logged in, but not allowed.
- *Follow-up: What does "stateless" mean?* Each request carries everything the server needs (a token or a cookie). The server keeps no memory of the client between requests. So any server copy can answer, and scaling is easy.
- *Follow-up: Design the URLs for tasks and their comments.* `GET /tasks`, `POST /tasks`, `GET /tasks/{id}`, `GET /tasks/{id}/comments`. Plural nouns, the method is the verb, filters go in the query.

## 2. Your first app and ASGI (lesson 2)

**Q: What happens between `uvicorn main:app` and your function running?**

**A:** Uvicorn, an ASGI server, listens on a port and reads the HTTP request. It calls the FastAPI app. FastAPI finds the matching route, checks the inputs with Pydantic, and calls your function. Then it turns the returned value into JSON and sends the response.

- *Follow-up: `def` or `async def` for a route?* Use `async def` only when everything slow inside can be awaited. Plain `def` runs in a thread pool, so slow code does not freeze the server.
- *Follow-up: Where does `/docs` come from?* FastAPI builds an OpenAPI description from your type hints and Pydantic models. It serves Swagger UI at `/docs` and ReDoc at `/redoc`.
- *Follow-up: Why use `0.0.0.0` in Docker?* `127.0.0.1` can only be reached from inside the container. `0.0.0.0` accepts connections from outside it.
- *Follow-up: How do you test without starting a server?* `TestClient(app)` calls the app inside Python.

## 3. Path and query parameters (lesson 3)

**Q: How does FastAPI decide where a parameter comes from?**

**A:** A name inside the path (`{task_id}`) is a path parameter. Other simple types (`int`, `str`, `bool`, enums) are query parameters. A Pydantic model is the request body. You can force a source with `Path()`, `Query()`, `Body()` or `Header()`.

- *Follow-up: Why is the answer `422` and not `400` for `/tasks/abc`?* The request is well-formed, but the data is not valid. FastAPI sends `422` with a list of errors and their `loc`.
- *Follow-up: You have `/users/me` and `/users/{user_id}`. Which goes first?* The fixed one (`/users/me`). Routes are matched in the order you write them.
- *Follow-up: Why put a maximum on `limit`?* A request with `limit=10000000` could load the whole table. Use `Query(le=100)`.

## 4. Request bodies and Pydantic (lesson 4)

**Q: What is mass assignment, and how do you prevent it?**

**A:** It means accepting fields that the client should not control, such as `is_admin` or `id`, and saving them. To prevent it, use an input schema that lists only the allowed fields, and add `extra="forbid"` so unknown fields are rejected.

- *Follow-up: Why have separate `Create`, `Update` and `Read` models?* Each job allows different fields. Separate models make the contract clear and keep internal fields private.
- *Follow-up: Pydantic v1 vs v2?* v2 has a core written in Rust (`pydantic-core`), so it is much faster. `model_dump()` and `model_validate()` replace the old `dict()` and `parse_obj()`.
- *Follow-up: Are Pydantic checks the same as type hints in plain Python?* No. Plain type hints are not enforced when the program runs. Pydantic reads the hints and then checks and converts the data.

## 5. Responses and errors (lesson 5)

**Q: How do you avoid leaking a password hash from `GET /users/1`?**

**A:** Use `response_model=UserOut`, where `UserOut` has no password field. FastAPI sends only the fields of that model. Do not rely on "I will just not return that key".

- *Follow-up: Which status codes for create, delete, update and duplicate?* `201` (often with a `Location` header), `204` (empty body), `200`, and `409 Conflict`.
- *Follow-up: How do you build PATCH correctly?* Make every field optional in the model, then use `payload.model_dump(exclude_unset=True)`. It separates "not sent" from "sent as null".
- *Follow-up: How do you keep error bodies consistent?* Always use `{"detail": ...}`, and maybe a machine-readable `code`. Never send stack traces to clients.

## 6. Project structure and settings (lesson 6)

**Q: How would you structure a FastAPI project, and why?**

**A:** `routes` (HTTP only) call `services` (business rules), which call `repositories` (storage). `schemas` hold the Pydantic models and `core` holds settings. Code points downward only. This makes the code easy to test, and you can change the storage without touching the routes.

- *Follow-up: Where do settings and secrets live?* In environment variables, read with `pydantic-settings`. Locally in a `.env` file that is not committed. In production, a secrets manager. Commit `.env.example`.
- *Follow-up: Why should a service not raise `HTTPException`?* It ties business logic to HTTP. Raise domain errors in services, and turn them into HTTP errors at the edge.
- *Follow-up: How do you version an API?* Use a prefix like `/api/v1` with `include_router(prefix=...)`. Breaking changes go to `/v2`.

## 7. Validation, forms and files (new lessons)

**Q: How do you add a custom rule to a Pydantic model, and when is a validator the wrong place?**

**A:** `@field_validator` for one field (clean or check, return the value, raise `ValueError`) and `@model_validator(mode="after")` for rules across fields. FastAPI sends the error as a `422`. Do not use a validator for rules that need the database (like "email is unique"). That belongs in the service layer, as a `409`.

- *What is a discriminated union?* A union of models where one field (`Literal`) tells which model to use: `Field(discriminator="channel")`. Faster, and the errors are clearer.
- *How do you accept a file upload safely?* `UploadFile`. Check the content type, limit the size (read `MAX + 1` bytes), use only the base name of the file, and store it outside the code folder. The client controls name, type and size.
- *Form, JSON or query?* A browser form sends form data (`Form()`), an API client sends JSON (a model), simple filters go in the query.
- *What do `httponly`, `secure` and `samesite` do on a cookie?* Hide it from JavaScript, send only over HTTPS, and limit sending on cross-site requests.

## 8. Quick answers

| Question | Short answer |
|---|---|
| Default status code of a FastAPI POST route | `200`, unless you set `status_code=201` |
| Body of a `204` response | empty |
| What `exclude_unset=True` does | keeps only the fields the client sent |
| Request body in a `GET` | not used; use query parameters |
| Status for "email already exists" | `409 Conflict` |
| Status for failed validation | `422` |
| Tool for testing an API in Python without a server | `TestClient` |
| ASGI vs WSGI | ASGI supports `async`; WSGI is the older, sync-only standard |
| What is OpenAPI | a machine-readable description of your API |

## Tools for the three coding exercises

Each exercise below is a small API. In an interview you may get 25 minutes for one. Here are the building blocks, shown on **different** problems from the ones in the exercises.

**Plan first.** Before you type, write down for each endpoint: the method, the path, the success code and the error codes. Then code one endpoint at a time and test it.

### Building block 1: a CRUD API in a dict (for the Notes API)

Store items in a module-level dict, with the id as the key. Make the next id from the largest existing key:

```python
TICKETS: dict[int, dict] = {}

new_id = max(TICKETS, default=0) + 1
print(new_id)                 # -> 1  (empty dict)
TICKETS[1] = {"id": 1, "text": "Fix login"}
print(max(TICKETS, default=0) + 1)   # -> 2
```

`default=0` is what `max` gives when the dict is empty. Without it, `max` raises an error.

Pattern for the routes:

```python
@app.post("/tickets", status_code=201)
def create_ticket(payload: TicketCreate):
    new_id = max(TICKETS, default=0) + 1
    TICKETS[new_id] = {"id": new_id, **payload.model_dump()}
    return TICKETS[new_id]

@app.delete("/tickets/{ticket_id}", status_code=204)
def delete_ticket(ticket_id: int):
    if ticket_id not in TICKETS:
        raise HTTPException(status_code=404, detail="Ticket not found")
    del TICKETS[ticket_id]
```

For a list with paging, sort by id and cut with a slice:

```python
items = sorted(TICKETS.values(), key=lambda t: t["id"])
page = items[offset : offset + limit]
```

For `PATCH`, remember lesson 5: `payload.model_dump(exclude_unset=True)` and `dict.update(...)`.

### Building block 2: rules on a signup body (for the Signup API)

A text rule with `pattern`, a length rule, and `extra="forbid"`:

```python
class ContactIn(BaseModel):
    model_config = ConfigDict(extra="forbid")

    phone: str = Field(pattern=r"^\d{10}$")      # exactly 10 digits
    nickname: str = Field(min_length=1, max_length=20)
```

In a pattern, `.+` means "one or more of any character", `\d` means a digit, and `\.` means a real dot. So `.+@.+\..+` means: something, `@`, something, a dot, something.

To compare text without caring about upper or lower case, change both sides with `.lower()`:

```python
saved = ["Ana@x.io"]
new_email = "ANA@X.IO"
print(any(e.lower() == new_email.lower() for e in saved))   # -> True
```

When it is a duplicate, raise `HTTPException(status_code=409, detail="...")`.

To never send a secret, give the route a `response_model` without that field (lesson 5).

### Building block 3: filter, sort and page a list (for the Product search)

Start with the full list. Filter step by step, then count, then sort, then cut the page:

```python
FILMS = [
    {"id": 1, "name": "avatar", "year": 2009},
    {"id": 2, "name": "Brave", "year": 2012},
    {"id": 3, "name": "cars", "year": 2006},
]

items = FILMS
year_from = 2008
if year_from is not None:
    items = [f for f in items if f["year"] >= year_from]   # filter

total = len(items)                                          # count BEFORE paging
items = sorted(items, key=lambda f: f["name"].lower())      # sort, ignoring case
page = items[0:10]                                          # offset 0, limit 10
print(total, [f["name"] for f in page])   # -> 2 ['avatar', 'Brave']
```

- To sort from big to small, add `reverse=True` to `sorted`.
- An `Enum` as a query parameter (lesson 3) gives you `422` for free when the value is not allowed.
- Check a rule like "min must not be bigger than max" at the start of the route, and raise `HTTPException(status_code=400, ...)`.
- A `limit` rule like `Annotated[int, Query(ge=1, le=100)] = 10` handles the numeric limits.

## How to practise

1. Do the three coding exercises below, **25 minutes each**.
2. Before you run the tests, say out loud which status codes and edge cases you handle.
3. Ask Claude to run a mock interview on this module, one question at a time.
