---
title: "API design: pagination, filtering, versioning"
summary: Design list endpoints that still work with lots of data, with pagination, filtering, sorting, versions and idempotency keys.
plan_ids: [BE-01, FA-08]
---

Your CRUD API works. Now make it **pleasant and safe when it grows**.

- A `GET /tasks` that returns 100,000 rows will time out.
- A client that retries a payment must not charge the customer twice.
- A change must not break every mobile app that is already installed.

These are the design questions interviewers ask after "build a CRUD API".

## Pagination: never return an unlimited list

**Pagination** means sending a long list in small pages. There are two common styles.

### Offset pagination

The client says how many items it wants (`limit`) and how many to skip (`offset`).

```text
GET /api/v1/tasks?limit=20&offset=40
```

The response is wrapped in an **envelope** (an object around the list), so it can carry extra information:

```json
{"items": ["...20 tasks..."], "total": 523, "limit": 20, "offset": 40}
```

In SQL it is two queries: one for the page and one for the total count.

```sql
SELECT ... ORDER BY id LIMIT 20 OFFSET 40;
SELECT COUNT(*) FROM tasks WHERE <the same filters>;
```

Good: simple, and a client can jump to any page ("page 3 of 27").

Bad:

- Deep pages are slow. `OFFSET 100000` still makes the database walk past 100,000 rows.
- While data changes, pages shift. If a new row is added, you may see an item twice or miss one.

### Cursor pagination

Instead of "skip N", the client says "continue **after this item**". The server gives back a **cursor**, which marks the position.

```text
GET /api/v1/events?limit=20                      -> {"items": [...], "next_cursor": "eyJpZCI6IDEyMH0"}
GET /api/v1/events?limit=20&cursor=eyJpZCI6IDEyMH0
```

```sql
SELECT ... WHERE id < :last_seen_id ORDER BY id DESC LIMIT 20;
```

Good:

- It is fast at any depth, because the database jumps straight to the position using the index.
- It is stable: new rows arriving at the top do not disturb the pages you are walking.
- It is the right choice for feeds, logs, chat, and infinite scroll.

Bad: you cannot jump to "page 37", and a total count is optional or slow.

The cursor should be **opaque**: the client must treat it as a meaningless string. A simple way is to encode the last id as base64:

```python
import base64
import json

def encode_cursor(last_id):
    return base64.urlsafe_b64encode(json.dumps({"id": last_id}).encode()).decode()

def decode_cursor(cursor):
    return json.loads(base64.urlsafe_b64decode(cursor))["id"]

c = encode_cursor(120)
print(c)                  # -> eyJpZCI6IDEyMH0=
print(decode_cursor(c))   # -> 120
```

Because the client does not look inside, you can change what the cursor contains later, without breaking anyone.

**Rule of thumb:** use offset for small data and admin tables. Use a cursor for large, fast-growing data and public APIs.

Two rules for both styles:

- **Always limit `limit`** (for example 1 to 100).
- **Always sort in a fixed way.** If you sort by `created_at` and two rows have the same time, add `id` as a second sort key (a **tie-breaker**). Without it, the database may order equal rows differently on each page, and pages overlap.

## A typed page envelope

A generic model can wrap any list:

```python
from pydantic import BaseModel

class Page[T](BaseModel):
    items: list[T]
    total: int
    limit: int
    offset: int
```

`Page[T]` is a **generic** class: `T` is a placeholder for the item type, like "a page of ... what?" You fill it in when you use it: `Page[Product]` means "a page of products".

```python
class Product(BaseModel):
    id: int
    name: str

page = Page[Product](items=[Product(id=1, name="Pen")], total=1, limit=10, offset=0)
print(page.model_dump())
# -> {'items': [{'id': 1, 'name': 'Pen'}], 'total': 1, 'limit': 10, 'offset': 0}
```

In a route: `@router.get("", response_model=Page[Product])`.

Why an envelope and not a plain list? An object can get new fields later (like `next_cursor`) without breaking clients. A bare list cannot.

## Worked example: a list endpoint with filter, search, sort and paging

Exercise 1 asks for exactly this kind of endpoint. Here is the same pattern for a different problem: **books**.

```python
BOOKS = [{"id": i, "title": f"Book {i}", "genre": "sci-fi" if i % 2 else "drama", "pages": 100 + i} for i in range(1, 31)]
```

Goal: `GET /books?genre=drama&q=1&sort=-pages&limit=5&offset=0` returns `{"items": [...], "total": ..., "limit": 5, "offset": 0}`.

**Step 1.** Make models and allowed sort values. A `Literal` type lists the allowed texts. Anything else gives `422` for free.

```python
from typing import Annotated, Literal
from fastapi import FastAPI, Query

BookSort = Literal["id", "-id", "pages", "-pages"]

class Book(BaseModel):
    id: int
    title: str
    genre: str
    pages: int
```

**Step 2.** Write the route with typed, limited parameters.

```python
app = FastAPI()

@app.get("/books", response_model=Page[Book])
def list_books(
    genre: str | None = None,
    q: Annotated[str | None, Query(max_length=50)] = None,
    sort: BookSort = "id",
    limit: Annotated[int, Query(ge=1, le=50)] = 10,
    offset: Annotated[int, Query(ge=0)] = 0,
):
```

**Step 3.** Filter step by step. Do the count **after** filtering and **before** paging.

```python
    items = BOOKS
    if genre is not None:
        items = [b for b in items if b["genre"] == genre]
    if q:
        items = [b for b in items if q.lower() in b["title"].lower()]
    total = len(items)
```

**Step 4.** Sort. A leading `-` means descending. Add `id` as the tie-breaker.

```python
    field = sort.lstrip("-")
    items = sorted(items, key=lambda b: (b[field], b["id"]), reverse=sort.startswith("-"))
```

`reverse=True` also reverses the tie-breaker, which is fine: it stays deterministic.

**Step 5.** Cut the page and return the envelope.

```python
    return {"items": items[offset : offset + limit], "total": total, "limit": limit, "offset": offset}
```

**Step 6.** Check it.

```python
client = TestClient(app)
r = client.get("/books?genre=drama&sort=-pages&limit=3").json()
print(r["total"], [b["id"] for b in r["items"]])   # -> 15 [30, 28, 26]
print(client.get("/books?sort=title").status_code)  # -> 422
```

## Filtering, searching and sorting

A typical request:

```text
GET /api/v1/tasks?done=false&priority=high&q=report&sort=-due_date
```

- **Filters**: one query parameter per field, with a type (`bool`, an `Enum`) so FastAPI validates it.
- **Search**: a parameter like `q` for text search. In SQL `ILIKE '%report%'` is fine for small tables. Big tables need full-text search or a search engine.
- **Sorting**: `sort=field` is ascending, `sort=-field` is descending. **Allow only a fixed list of fields** (use a `Literal` or `Enum`). Never put user input straight into `ORDER BY`. That is unsafe and may be slow on columns without an index.

## Versioning

Some clients (mobile apps, partners) cannot update quickly. So you put a **version** in your API and never break a published version.

| Style | Example |
|---|---|
| In the URL path (the most common) | `/api/v1/tasks`, then `/api/v2/tasks` |
| In a header | `Accept: application/vnd.taskflow.v2+json` |
| In the query | `?version=2` |

What is a **breaking change**? Anything that can break existing clients:

- removing or renaming a field,
- changing a field's type,
- making an optional field required,
- changing the error format or a status code.

These are **not** breaking: adding a new optional field, or adding a new endpoint.

To end an old version, announce a date, and send `Deprecation` and `Sunset` headers.

## Idempotency keys

Remember lesson 1: `POST` is not idempotent. Picture this: a client sends `POST /payments`. The server creates the payment, but the network drops before the client gets the answer. The client retries, and the customer pays twice.

The fix (used by payment companies) is an **idempotency key**. The client creates a unique value and sends it in a header:

```text
POST /payments
Idempotency-Key: 7f9c2b1e-...
```

The server follows these rules:

1. Key **found** and the body is the **same**: do not run it again. Return the **saved response**.
2. Key found but the body is **different**: reject it. The client reused a key by mistake.
3. Key **not found**: do the work, save `(key, request body, response)`, and return the response.

Here is the idea on a small example with **orders**:

```python
STORE = {}        # key -> (body, response)
ORDERS = []

@app.post("/orders", status_code=201)
def create_order(body: OrderIn, idempotency_key: Annotated[str | None, Header()] = None):
    data = body.model_dump()
    if idempotency_key in STORE:
        saved_body, saved_response = STORE[idempotency_key]
        if saved_body != data:
            raise HTTPException(422, "Idempotency-Key reused with a different request")
        return saved_response
    order = {"id": len(ORDERS) + 1, **data}
    ORDERS.append(order)
    if idempotency_key is not None:
        STORE[idempotency_key] = (data, order)
    return order
```

A second request with the same key and body returns the same order, and `ORDERS` does not grow.

In a real system the store is Redis or a database table. The key column is unique, so two retries arriving at the same moment cannot both win.

## A little deeper (optional)

- **Cursor with a sorted field.** If you sort by something other than `id`, the cursor must hold both the sort value and the `id` (to break ties).
- **Why cursors survive new rows.** The query says `id < last_seen_id`. A new event gets a bigger id and appears at the top, so it never shifts the pages you are walking.
- **Other good habits**: use `snake_case` names in JSON, plural nouns in URLs, ISO 8601 timestamps in UTC, `201` plus a `Location` header on create, and `204` on delete.
- **Rate limits** (Level 3) protect the API from a client that sends too many requests.

## Common mistakes

- A list endpoint with no limit, or a `limit` with no maximum.
- No fixed order. Pages then overlap.
- Building `ORDER BY` from raw user input.
- Breaking a published version "just a little".
- Retrying a `POST` with no idempotency key.

## Interview corner

- **Q: Offset or cursor pagination?** Offset is simple and can jump to any page, but deep pages are slow and the pages can shift when data changes. A cursor is fast, stable, and uses the index, but has no random access.
- **Q: How do you stop double charges when a client retries?** Use idempotency keys. Save the key, the request and the response. On a retry, send back the saved response.
- **Q: What is a breaking change, and how do you ship one?** Removing or renaming fields, or changing their meaning. Release it as a new version, keep the old one running, and announce a deprecation date.
- **Q: How do you let users sort safely?** Allow only a fixed list of fields, map them to columns, add a tie-breaker, and make sure those columns are indexed.

## Summary

- Always paginate. Limit the `limit`. Sort in a fixed way.
- Offset for small or simple data. A cursor for large or growing data.
- Return an envelope: `items`, `total`, `limit`, `offset` (or `next_cursor`).
- Typed filters, a `q` search, and a whitelisted `sort` where `-field` means descending.
- Put the version in the URL. Never break a published version.
- Idempotency keys make `POST` retries safe.
