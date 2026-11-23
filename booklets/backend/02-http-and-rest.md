# 2. HTTP and REST

Every talk between a client and a backend uses HTTP. If you understand HTTP well, half of backend work becomes easy, because most bugs are "the request was not what we thought".

**REST** is a set of habits for designing APIs on top of HTTP, so that every API feels familiar. This chapter covers both.

## Anatomy of a request and a response

@@ flow | Figure 2.1: what travels in each direction.
Request|method + path;headers;body (optional)|blue <-> Response|status code;headers;body (optional)|green
@@ end

| Part | Example | What it means |
| --- | --- | --- |
| Method | `POST` | the action |
| Path | `/orders/15` | which thing |
| Query string | `?status=paid&page=2` | extra filters after the `?` |
| Headers | `Authorization: Bearer abc123` | facts about the request |
| Body | `{"item": "pizza", "qty": 2}` | the data you send (JSON) |

A full example. The client creates an order:

```
POST /orders HTTP/1.1
Host: api.example.com
Content-Type: application/json
Authorization: Bearer abc123

{"item": "pizza", "qty": 2}
```

The server answers:

```
HTTP/1.1 201 Created
Content-Type: application/json
Location: /orders/15

{"id": 15, "item": "pizza", "qty": 2, "status": "new"}
```

`201` says "created". `Location` tells the client where the new item lives.

## Methods: what each one means

Think of a notebook of orders. `GET` reads the notebook. `POST` adds a new line. `PUT` rewrites a whole line. `PATCH` fixes a few words in a line. `DELETE` strikes a line out.

| Method | Use | Safe | Idempotent |
| --- | --- | --- | --- |
| `GET` | read | yes | yes |
| `POST` | create / run an action | no | no |
| `PUT` | replace the whole item | no | yes |
| `PATCH` | change some fields | no | usually no |
| `DELETE` | remove | no | yes |

**Safe** means it does not change anything on the server. **Idempotent** means doing it many times has the same effect as doing it once.

Why does idempotent matter? Networks fail. If a client sends a request and gets no answer, it does not know if the server got it. If the method is idempotent, the client can safely send it again.

> `DELETE /orders/15` twice: the first deletes, the second finds nothing. The end state is the same (no order 15), so `DELETE` is idempotent. `POST /orders` twice makes two orders, so `POST` is not.

### Making POST safe to retry: idempotency keys

For things like payments, a double `POST` is a disaster. The fix: the client sends a unique key, and the server remembers it.

```
POST /payments
Idempotency-Key: 7f3a-91bc

{"amount": 500}
```

The server stores the key with the result. If the same key arrives again, it returns the stored result and does not charge twice.

## Status codes

The first digit tells the story.

@@ grid 5 | Figure 2.2: the five families.
1xx|info|gray
2xx|success|green
3xx|redirect|blue
4xx|client made a mistake|yellow
5xx|server made a mistake|red
@@ end

| Code | Name | When to use |
| --- | --- | --- |
| `200` | OK | normal success |
| `201` | Created | a new item was made |
| `202` | Accepted | "got it, I will do it later" (queues, chapter 9) |
| `204` | No Content | success, nothing to return |
| `301` / `302` | Redirect | the thing moved |
| `304` | Not Modified | your cached copy is still good |
| `400` | Bad Request | broken request |
| `401` | Unauthorized | not logged in |
| `403` | Forbidden | logged in, but not allowed |
| `404` | Not Found | no such item |
| `409` | Conflict | clashes with current state (duplicate) |
| `422` | Unprocessable Entity | right format, wrong values |
| `429` | Too Many Requests | slow down |
| `500` | Internal Server Error | a bug in your code |
| `502` / `503` / `504` | Bad gateway / Unavailable / Timeout | a server behind another one is down or slow |

> **401 vs 403** is a classic interview question. `401`: "I do not know who you are." `403`: "I know who you are, and you may not do this."

## Headers you will meet often

| Header | Direction | Purpose |
| --- | --- | --- |
| `Content-Type` | both | format of the body (`application/json`) |
| `Accept` | request | the format the client wants back |
| `Authorization` | request | login proof, e.g. `Bearer <token>` |
| `Cache-Control` | response | how long a copy may be kept |
| `ETag` | response | a fingerprint of the data, used to check "did it change?" |
| `Retry-After` | response | seconds to wait after a `429` or `503` |
| `Location` | response | where the new or moved item is |
| `Origin` | request | which website sent the request (CORS) |

## REST: design habits

REST says: think in **resources** (things, as nouns), and use methods as the verbs.

| Task | Good | Bad |
| --- | --- | --- |
| list orders | `GET /orders` | `GET /getAllOrders` |
| one order | `GET /orders/15` | `GET /order?id=15` (works, but less clean) |
| create | `POST /orders` | `POST /createOrder` |
| replace | `PUT /orders/15` | `POST /updateOrder` |
| delete | `DELETE /orders/15` | `GET /deleteOrder/15` |
| orders of a user | `GET /users/7/orders` | `GET /userOrders?u=7` |

Rules of thumb:

- Use **plural nouns** (`/orders`), lowercase, with hyphens.
- A **GET never changes data.** Crawlers and browsers may call it at any time.
- Return the **right status code** and a **consistent error shape**, for example `{"error": "not_found", "message": "Order 15 does not exist"}`.
- Not everything fits. For an action like "cancel", `POST /orders/15/cancel` is fine and common.

## Filtering, sorting and pagination

A list can be huge. Never return all of it.

```
GET /orders?status=paid&sort=-created_at&limit=20&offset=40
```

Two ways to paginate:

| Style | How | Good | Bad |
| --- | --- | --- | --- |
| **Offset** | `?limit=20&offset=40` | easy, can jump to page 5 | slow on big offsets; items can shift if data changes |
| **Cursor** | `?limit=20&after=<last_id>` | fast, stable when data changes | cannot jump to page 5 |

> Use offset for small admin tables. Use cursor for feeds and big lists.

## Versioning

Once clients use your API, changing it can break them. Put a version in the path: `/api/v1/orders`. When you must make a breaking change, ship `/api/v2` and keep `v1` running for a while.

Breaking: removing a field, renaming a field, changing a type. Not breaking: adding a new optional field.

## HTTPS and CORS in two minutes

- **HTTPS** is HTTP inside an encrypted tunnel (TLS). Without it, anyone on the network can read passwords. Always use it in production.
- **CORS**: a browser rule. A page on `site-a.com` may not call `api-b.com` unless `api-b.com` says it is allowed. The server allows it with headers like `Access-Control-Allow-Origin`. It protects users in browsers. It does **not** protect your API from scripts or curl.

::: {.box .fastapi}
**How FastAPI does this**

- Method and path: `@app.get("/orders/{order_id}")`, `@app.post("/orders", status_code=201)`.
- Query string: a function argument, `def list_orders(limit: int = 20, offset: int = 0)`.
- Headers: `Header()`. Body: a Pydantic model. Errors: `raise HTTPException(404)`.
- CORS: `CORSMiddleware`. Versioning: `APIRouter(prefix="/api/v1")`.
- Wrong input becomes a `422` automatically.
:::

## Common mistakes

::: {.box .mistake}
**Common mistakes**

- Changing data on a `GET` request.
- Always returning `200`, even with `{"success": false}` inside.
- Using `401` when you mean `403`, or the other way round.
- Returning an unbounded list (no limit).
- Breaking a field name in `v1` without a new version.
- Thinking CORS secures the API. It only guides browsers.
:::

## Interview corner

::: {.box .interview}
**Interview corner**

**Q: What does idempotent mean? Which methods are idempotent?**
Repeating the request gives the same end state as sending it once. `GET`, `PUT` and `DELETE` are idempotent. `POST` is not. We use idempotency keys to make `POST` safe to retry.

**Q: PUT vs PATCH?**
`PUT` replaces the whole item. `PATCH` changes only the fields you send.

**Q: 401 vs 403?**
`401`: not authenticated (we do not know you). `403`: authenticated but not allowed.

**Q: Offset vs cursor pagination?**
Offset is simple but slow for large offsets and unstable when rows change. Cursor is fast and stable but you cannot jump to an arbitrary page.

**Q: What is REST?**
A style of API design: resources named with nouns in URLs, standard HTTP methods as verbs, stateless requests and proper status codes.
:::

## Exercises

::: {.box .exercise}
**Exercises**

1. Which HTTP method and URL would you use to: (a) list a user's comments, (b) add a comment, (c) edit only the text of a comment, (d) delete a comment?
2. A client sent `POST /payments` and the connection dropped before any answer. Why is just retrying dangerous, and how does an idempotency key fix it?
3. Pick the status code: (a) a user forgot to log in, (b) a normal user opens the admin page, (c) the email already exists, (d) the JSON is valid but `age` is `-5`, (e) your code crashed.
4. Fix these bad URLs: `GET /getUser?id=5`, `POST /deleteOrder/9`, `GET /Orders_List`.
5. **Think:** a feed has new posts every second. Why would offset pagination show the same post twice on page 2?
:::
