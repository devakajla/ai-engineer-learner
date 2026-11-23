---
title: "How the web works: HTTP & REST"
summary: What a client sends to an API, what the API sends back, and the simple rules (REST) that backend developers follow.
plan_ids: [BE-01]
---

Before you write any FastAPI code, you need a clear picture of **what an API receives and what it sends back**. FastAPI hides many details. That is nice when you are building. But when something breaks, or when an interviewer asks, you must know what is happening underneath.

This lesson has no FastAPI yet. It is only the ideas. Take your time with it.

> **About this track.** Every lesson has: theory, a quiz, small exercises, and a **project step**. Step by step you will build **TaskFlow**, a real task-manager API, in your own folder. The app checks each step with hidden tests, then Claude reviews your code.

## What is an API?

An **API** is a way for one program to talk to another program.

Think of a restaurant. You (the **client**) do not walk into the kitchen. You tell the waiter what you want. The waiter goes to the kitchen (the **server**), and brings your food back.

In our case:

- The **client** is any program that asks for something: a browser, a phone app, `curl`, or another server.
- The **server** is the program that answers. The server is what you will build with FastAPI.

## Request and response

All of the web works like this:

1. The client sends a **request**: "please do this".
2. The server runs some code and sends back one **response**: "here is the result".

That is all. One request, one response.

HTTP is also **stateless**. This means the server does not remember earlier requests. Each request must carry everything the server needs, for example who you are. (Later you will learn how logins work with this rule.)

## What an HTTP request looks like

An HTTP request is just text. Here is a real one:

```http
POST /tasks?notify=true HTTP/1.1
Host: api.taskflow.dev
Content-Type: application/json
Authorization: Bearer abc123

{"title": "Write tests", "priority": "high"}
```

Let us read it piece by piece.

| Part | In the example | Meaning |
|---|---|---|
| Method | `POST` | What do you want to do? |
| Path | `/tasks` | Which thing do you want to do it to? |
| Query string | `?notify=true` | Extra options. Written as `key=value`. Many options are joined with `&`. |
| Version | `HTTP/1.1` | Which version of HTTP |
| Headers | `Content-Type: application/json` | Extra information, one `Name: value` per line |
| Body | `{"title": ...}` | The data you send. Optional. |

The first line (method, path with query, version) is called the **request line**. A blank line separates the headers from the body.

The response has the same shape: a **status line**, then headers, then an optional body.

```http
HTTP/1.1 201 Created
Content-Type: application/json
Location: /tasks/42

{"id": 42, "title": "Write tests", "priority": "high", "done": false}
```

The status line has three parts: the version, the **status code** (`201`), and a short reason (`Created`).

## Reading a request line with Python

You will do this in the first exercise, so let us practice the tools on a similar problem: reading a **status line**.

Goal: turn `"HTTP/1.1 404 Not Found"` into a dictionary.

**Step 1.** Split the text on spaces, but only at the first two spaces. The reason (`Not Found`) has a space inside it, and we want to keep it as one piece.

```python
line = "HTTP/1.1 404 Not Found"
parts = line.split(" ", 2)   # 2 means: at most 2 splits
print(parts)                 # -> ['HTTP/1.1', '404', 'Not Found']
```

**Step 2.** Put the pieces in a dictionary. The code should be a number, so convert it with `int`.

```python
version, code, reason = parts
result = {"version": version, "code": int(code), "reason": reason}
print(result)   # -> {'version': 'HTTP/1.1', 'code': 404, 'reason': 'Not Found'}
```

Another useful tool is `partition`. It cuts a string into three pieces around the **first** match: the part before, the separator itself, and the part after.

```python
print("/tasks?done=true".partition("?"))   # -> ('/tasks', '?', 'done=true')
print("/tasks".partition("?"))             # -> ('/tasks', '', '')
```

If the separator is not found, you get the whole text and two empty strings. This makes `partition` a good tool for splitting a path from its query string, even when there is no query.

To read a query string like `done=true&limit=5`, split on `&` first to get each pair, then split every pair on `=`.

```python
query = "done=true&limit=5"
result = {}
for pair in query.split("&"):
    key, _, value = pair.partition("=")
    result[key] = value
print(result)   # -> {'done': 'true', 'limit': '5'}
```

Notice that the values are strings (`"5"`, not `5`). Everything that comes in through a URL is text.

## HTTP methods

The **method** is the verb of the request. It tells the server what you want to do.

| Method | Use it to | Safe? | Idempotent? | Has a body? |
|---|---|---|---|---|
| `GET` | read data | yes | yes | no |
| `POST` | create something, or start an action | no | no | yes |
| `PUT` | replace a whole thing | no | yes | yes |
| `PATCH` | change only some fields | no | usually no | yes |
| `DELETE` | delete | no | yes | rarely |

Two new words are in this table.

**Safe** means: the request does not change anything on the server. A `GET` only reads. Browsers may repeat or prefetch safe requests whenever they like, because nothing can go wrong.

**Idempotent** means: doing the request **once, or ten times, leaves the server in the same final state**.

- `DELETE /tasks/5` twice: the task is gone after the first call. After the second call it is still gone. The state is the same. (The second response may be `404`, because the task is already missing. But idempotent is about the **state** on the server, not the response.)
- `POST /tasks` twice: you get **two** tasks. The state is different. So `POST` is **not** idempotent.

Why does this matter? Networks fail. When a request times out, clients and load balancers often **try again**. Repeating an idempotent request is safe. Repeating a `POST` can create duplicates. (Later you will learn a fix called an *idempotency key*.)

## Status codes

Every response has a **status code**: a number that tells the client how it went. The first digit tells the group.

| Group | Meaning | Codes to know |
|---|---|---|
| 1xx | information | rare in APIs |
| 2xx | **success** | `200 OK`, `201 Created`, `204 No Content` |
| 3xx | redirect ("look somewhere else") | `301 Moved Permanently`, `304 Not Modified` |
| 4xx | the **client** made a mistake | `400 Bad Request`, `401 Unauthorized`, `403 Forbidden`, `404 Not Found`, `409 Conflict`, `422 Unprocessable Entity`, `429 Too Many Requests` |
| 5xx | the **server** failed | `500 Internal Server Error`, `502 Bad Gateway`, `503 Service Unavailable`, `504 Gateway Timeout` |

A simple way to remember: **4xx = your fault, 5xx = our fault.**

A few codes in plain words:

- `200` OK: it worked.
- `201` Created: it worked, and a new thing now exists.
- `204` No Content: it worked, and there is nothing to send back (common after a delete).
- `404` Not Found: no such thing.
- `409` Conflict: the request clashes with the current state (for example, that email is already taken).
- `429` Too Many Requests: slow down.

Two classic questions that confuse many people:

- **401 vs 403.** `401` means "I do not know who you are" (no login, or a bad login). `403` means "I know who you are, but you are not allowed to do this".
- **400 vs 422.** FastAPI uses `422` when the JSON is correct JSON, but the values do not pass the rules. For example, `priority` must be `"low"` or `"high"`, but the client sent `"urgent"`.

## Headers you will see every day

Headers are small notes that travel with a request or response.

- `Content-Type`: what format the body is in (`application/json`).
- `Accept`: what format the client wants back.
- `Authorization`: login information, for example `Bearer <token>`.
- `Location`: where a newly created thing lives (sent with `201`).
- `X-Request-ID`: a custom header used to follow one request through the logs.

## JSON

APIs mostly send data as **JSON**. It looks like a Python dictionary and list, and it maps to Python very easily:

| JSON | Python |
|---|---|
| object `{}` | `dict` |
| array `[]` | `list` |
| string | `str` |
| number | `int` or `float` |
| `true` / `false` | `True` / `False` |
| `null` | `None` |

Turning Python data into JSON text is called **serialization**. Turning JSON text back into Python data is **deserialization**.

## REST: a tidy way to design an API

**REST** is a set of habits for designing HTTP APIs. The idea: your API is built around **things** (called *resources*, such as tasks or users). The URL names the thing. The method says what to do with it.

For a `tasks` resource:

| Action | Method + path | Success code |
|---|---|---|
| List all tasks | `GET /tasks` | 200 |
| Create a task | `POST /tasks` | 201 |
| Read one task | `GET /tasks/{id}` | 200 |
| Replace a task | `PUT /tasks/{id}` | 200 |
| Change some fields | `PATCH /tasks/{id}` | 200 |
| Delete a task | `DELETE /tasks/{id}` | 204 |

`{id}` means "the id of the task goes here", for example `/tasks/42`.

Habits to follow:

- **Use plural nouns** in paths: `/tasks`, not `/getTasks` or `/task/create`. The method is already the verb.
- **Path says which thing, query says options.** `/tasks/42` is one task. `/tasks?done=true&limit=20` is a filtered list.
- **Nest** when one thing belongs to another: `/projects/7/tasks`. Keep it to one level.
- **Add a version** to the path: `/api/v1/tasks`. You will do this in lesson 6.
- **Use status codes** to tell the result. Do not send `200` with `{"success": false}`.

## A little deeper (optional)

- **PUT vs PATCH.** `PUT` replaces the whole thing, so the client sends every field. `PATCH` changes only the fields that are sent. Because `PUT` sets the full state, repeating it gives the same result, so it is idempotent.
- **Why is `PATCH` "usually not" idempotent?** `{"op": "add 1 to counter"}` changes the state every time. But `{"done": true}` is the same every time. It depends on what the patch says.
- **HTTP/1.1 is text.** Newer versions (HTTP/2) send the same ideas in a binary format. Your code does not change.

## Common mistakes

- Using `GET` to change data, like `GET /tasks/5/delete`. Search crawlers and browser prefetch will follow that link and delete your data.
- Returning `200` for every answer and hiding errors inside the body.
- Putting verbs in the URL: `/createTask`.
- Mixing up `401` (who are you?) and `403` (you may not).
- Forgetting that query values are always text. `"5"` is not `5`.

## Interview corner

- **Q: What is the difference between PUT and PATCH?** `PUT` replaces the whole resource, so you send every field. `PATCH` updates only the fields you send.
- **Q: Is POST idempotent? How can you make "create" safe to retry?** No. The client sends an `Idempotency-Key` header. The server saves the key with the result, and on a retry it returns the saved result instead of creating again.
- **Q: What does "HTTP is stateless" mean? How do logins work then?** Each request stands alone. A login works because the client sends proof of identity with every request, such as a cookie or a token in the `Authorization` header.

## Summary

- A request = method + path + query + headers + optional body. A response = status code + headers + optional body.
- HTTP is stateless: every request carries what the server needs.
- Safe methods do not change data. Idempotent methods are safe to repeat: `GET`, `PUT`, `DELETE` yes; `POST` no.
- 2xx = success, 4xx = client mistake, 5xx = server failure. Know 200, 201, 204, 400, 401, 403, 404, 409, 422, 429, 500, 503.
- REST: plural nouns, path for which thing, query for options, method for the action, status code for the result.
- In Python, `split` and `partition` are enough to read a request line and a query string.
