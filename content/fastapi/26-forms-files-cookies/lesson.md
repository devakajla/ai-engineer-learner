---
title: "Forms, file uploads & cookies"
summary: Read HTML form data, uploaded files, cookies and headers, and send answers that are not JSON (HTML, redirects, downloads).
plan_ids: [FA-01]
---

So far every request body was **JSON** and every answer was JSON. The real web has more:

- A browser login page sends a **form**, not JSON.
- A user uploads a **photo**.
- The server remembers a login in a **cookie**.
- Some answers are an **HTML page**, a **redirect**, or a **file to download**.

This lesson covers each one with a small example.

> You need the package `python-multipart` for forms and uploads. In this app it is already installed. In your own project run `uv add python-multipart`.

## Form data

An HTML form sends its fields as text in a special format (not JSON). In FastAPI, mark each field with `Form()`:

```python
from typing import Annotated
from fastapi import FastAPI, Form
from fastapi.testclient import TestClient

app = FastAPI()

@app.post("/subscribe")
def subscribe(email: Annotated[str, Form()], plan: Annotated[str, Form()] = "free"):
    return {"email": email, "plan": plan}

client = TestClient(app)
print(client.post("/subscribe", data={"email": "a@x.io"}).json())
# -> {'email': 'a@x.io', 'plan': 'free'}
```

- In a test, `data={...}` sends **form data**. `json={...}` sends JSON.
- A Pydantic model is read from JSON. So for a form, list each field with `Form()`.
- Form fields are still checked. A missing `email` gives `422`.
- A route cannot read both a JSON body and form fields. The client picks one format.

```python
print(client.post("/subscribe", json={"email": "a@x.io"}).status_code)   # -> 422
```

## Cookies and headers

A **cookie** is a small piece of text that the server gives the browser. The browser sends it back on every later request. This is how a site "remembers" you. (How to do login safely comes in Level 3.)

**Read** a cookie with `Cookie()`. **Set** one with `response.set_cookie(...)`:

```python
from fastapi import Cookie, Response

@app.get("/visit")
def visit(response: Response, visits: Annotated[int, Cookie()] = 0):
    response.set_cookie("visits", str(visits + 1))
    return {"visits": visits + 1}

client = TestClient(app)
print(client.get("/visit").json())   # -> {'visits': 1}
print(client.get("/visit").json())   # -> {'visits': 2}
```

`TestClient` keeps cookies like a browser, so the second call sends `visits=1`.

A parameter named `response: Response` gives you the answer object, so you can add cookies or headers before FastAPI sends it. You still `return` your normal data.

Important flags for `set_cookie`:

| Flag | Meaning |
|---|---|
| `httponly=True` | JavaScript on the page cannot read the cookie. Use it for login cookies. |
| `secure=True` | The browser sends it only over HTTPS. |
| `samesite="lax"` | The browser does not send it on most requests started by other sites. |
| `max_age=3600` | The cookie lives 3600 seconds. Without it, it ends when the browser closes. |

A **header** is a line of extra information in a request, like `User-Agent` or `X-Request-Id`. Read it with `Header()`. A header name with dashes is written with underscores in Python:

```python
from fastapi import Header

@app.get("/agent")
def agent(user_agent: Annotated[str | None, Header()] = None):
    return {"agent": user_agent}

print(client.get("/agent", headers={"User-Agent": "demo"}).json())   # -> {'agent': 'demo'}
```

`user_agent` is matched to the header `User-Agent`.

## File uploads

For a file, use a parameter of type `UploadFile`:

```python
from fastapi import UploadFile

@app.post("/upload")
def upload(file: UploadFile):
    data = file.file.read()
    return {"name": file.filename, "type": file.content_type, "size": len(data)}

r = client.post("/upload", files={"file": ("a.txt", b"hello", "text/plain")})
print(r.json())   # -> {'name': 'a.txt', 'type': 'text/plain', 'size': 5}
```

- In a test, `files={"field": (name, bytes, content_type)}` sends a file.
- `file.filename` is the name the client gave. `file.content_type` is the type the client claimed.
- `file.file` is a file-like object. `.read()` gives the bytes. (`await file.read()` also works inside `async def`.)
- A big upload is kept on disk, not all in memory.

### Never trust an upload

The client controls the file name, the content type and the size. So:

1. **Check the type** against a short allowed list. For strong checks, look at the real first bytes of the file (a PNG starts with `\x89PNG`).
2. **Limit the size.** Read at most `MAX + 1` bytes: `file.file.read(MAX + 1)`. If you got more than `MAX`, answer `413`.
3. **Clean the file name.** A client may send `../../etc/passwd`. Use only the base name (`os.path.basename(name)`), or better, make your own name (a random id).
4. **Do not run or serve** uploaded files as code.

## Worked example: check an upload, step by step

Exercise 2 asks for checks on an uploaded image. Here is the same pattern for a different problem: upload a **text note** (`.txt`).

Rules, in this order:

1. The content type must be `text/plain`. Else `415`.
2. The file must be at most 100 bytes. Else `413`.
3. Answer `201` with `{"name": <base name>, "lines": <number of lines>}`.

**Step 1.** Constants and the route.

```python
import os

MAX_NOTE = 100

@app.post("/notes", status_code=201)
def upload_note(file: UploadFile):
```

**Step 2.** Check the type **first**. It is cheap, and you do not need to read the file for a wrong type.

```python
    if file.content_type != "text/plain":
        raise HTTPException(status_code=415, detail="Only text files")
```

**Step 3.** Read **one byte more** than the limit. This way you know the file is too big, without loading a huge file.

```python
    data = file.file.read(MAX_NOTE + 1)
    if len(data) > MAX_NOTE:
        raise HTTPException(status_code=413, detail="Note too large")
```

**Step 4.** Clean the name and build the answer.

```python
    name = os.path.basename(file.filename or "")
    return {"name": name, "lines": len(data.decode().splitlines())}
```

(`HTTPException` comes from `fastapi`, as in lesson 5.)

**Step 5.** Try it.

```python
r = client.post("/notes", files={"file": ("../a.txt", b"one\ntwo\n", "text/plain")})
print(r.status_code, r.json())   # -> 201 {'name': 'a.txt', 'lines': 2}
r = client.post("/notes", files={"file": ("big.txt", b"x" * 101, "text/plain")})
print(r.status_code)             # -> 413
r = client.post("/notes", files={"file": ("a.png", b"x", "image/png")})
print(r.status_code)             # -> 415
```

The order matters: the cheapest check first, then the one that reads data.

## Answers that are not JSON

By default FastAPI turns what you return into JSON. For other kinds of answers, use a **response class** from `fastapi.responses`.

| Class | Use |
|---|---|
| `HTMLResponse` | an HTML page |
| `PlainTextResponse` | plain text, with no JSON quotes |
| `RedirectResponse` | send the browser to another URL |
| `FileResponse` | send a file from disk (a download) |
| `JSONResponse` | JSON with a custom status code or headers |

```python
from fastapi.responses import HTMLResponse, PlainTextResponse, RedirectResponse

@app.get("/hello", response_class=HTMLResponse)
def hello():
    return "<h1>Hello</h1>"

@app.get("/health.txt", response_class=PlainTextResponse)
def health_txt():
    return "ok"

@app.get("/home")
def home():
    return RedirectResponse("/hello", status_code=301)

print(client.get("/hello").headers["content-type"])      # -> text/html; charset=utf-8
print(client.get("/health.txt").text)                     # -> ok
print(client.get("/home", follow_redirects=False).status_code)   # -> 301
```

- `response_class=HTMLResponse` sets the content type. Without it, the returned string would become a JSON string (with quotes).
- A redirect needs a `Location` header. `RedirectResponse(url, status_code=...)` does it. Use `301` or `308` for "moved forever", `302` or `307` for "temporary". (`307` and `308` keep the HTTP method. `301` and `302` may turn a `POST` into a `GET`.)
- `FileResponse(path, filename="report.txt")` streams a file and adds a header that makes the browser **download** it.

```python
from pathlib import Path
from fastapi.responses import FileResponse

@app.get("/report")
def report():
    return FileResponse(Path(__file__).parent / "report.txt", filename="report.txt")
```

If you return a response object yourself, FastAPI sends it as it is. It does not check it against a `response_model`.

## Leaving fields out of a JSON answer

You know `response_model` (lesson 5) hides fields that are not in the model. Sometimes you also want to leave out fields **whose value is `None`**, or fields that were not set. There are options on the decorator:

```python
from pydantic import BaseModel

class Profile(BaseModel):
    id: int
    name: str
    bio: str | None = None

@app.get("/profile", response_model=Profile, response_model_exclude_none=True)
def profile():
    return {"id": 1, "name": "Ana", "bio": None}

print(client.get("/profile").json())   # -> {'id': 1, 'name': 'Ana'}
```

- `response_model_exclude_none=True` drops fields that are `None`.
- `response_model_exclude_unset=True` drops fields that the code did not set (useful for `PATCH`-like answers).
- `response_model_exclude={"bio"}` always drops the named fields.

Do not use `response_model_exclude` to hide secrets. A separate output model (like `UserOut` without `password_hash`) is safer, because a new field can never leak by mistake.

## Backend concept: the browser world and the API world

Two kinds of clients call a backend:

- A **browser** with HTML forms, cookies and downloads. It sends form data and cookies by itself.
- An **API client** (mobile app, another service, a script). It sends JSON and usually an `Authorization` header.

Many backends serve both. Knowing the formats (JSON, form, multipart upload) helps you pick the right one. A rule of thumb: JSON for APIs, form and multipart only when a browser form or an upload needs them.

## A little deeper (optional)

- **Multipart.** A file upload uses the content type `multipart/form-data`. It can carry files **and** form fields in one request: `file: UploadFile, title: Annotated[str, Form()]`.
- **Many files.** Use `files: list[UploadFile]`.
- **`bytes` instead of `UploadFile`.** `file: Annotated[bytes, File()]` reads the whole file into memory. Fine for tiny files only.
- **Streaming big downloads.** `FileResponse` already streams. For generated data you can use `StreamingResponse` (Level 3).
- **Where to keep uploads.** In a real system, store files in object storage (such as S3) and keep only the link in the database.

## Common mistakes

- Using a Pydantic model for form data, or `data=` and `json=` mixed up in tests.
- Trusting `filename` and `content_type`.
- Reading a whole large upload before checking its size.
- Forgetting `httponly` on a login cookie.
- Returning HTML as a plain string and wondering why the browser shows quotes. Add `response_class=HTMLResponse`.
- Using `response_model_exclude` to hide secrets.

## Interview corner

- **Q: How do you accept a file upload in FastAPI?** Use `UploadFile` (needs `python-multipart`). Check the type and the size, clean the filename, and store the file outside your code folder.
- **Q: `UploadFile` or `bytes`?** `UploadFile` keeps large files on disk and gives a file-like object. `bytes` loads everything into memory.
- **Q: What do `httponly`, `secure` and `samesite` do on a cookie?** `httponly` hides it from JavaScript. `secure` sends it only over HTTPS. `samesite` limits sending it on requests started by other sites (helps against CSRF).
- **Q: How do you return an HTML page or a file download?** `response_class=HTMLResponse`, or return `FileResponse(path, filename=...)`.

## Summary

- `Form()` reads form fields. A Pydantic model reads only JSON.
- `Cookie()` and `Header()` read them. `response.set_cookie(...)` sets a cookie. Use `httponly=True` for login cookies.
- `UploadFile` reads an upload. Never trust its name, type or size: check them, in the cheapest-first order.
- Response classes: `HTMLResponse`, `PlainTextResponse`, `RedirectResponse`, `FileResponse`.
- `response_model_exclude_none` and friends shape the JSON. Use a separate output model to hide secrets.
