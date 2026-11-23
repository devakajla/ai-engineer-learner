# 14. Forms, file uploads, cookies and headers

JSON is not the only way data arrives. Web forms send **form fields**. Users upload **files**. Browsers keep **cookies**. Clients send **headers**. FastAPI reads each one in the same style you already know: a function argument with a type.

## Which one is it?

| Source | Use | Needs package |
| --- | --- | --- |
| JSON body | a Pydantic model | none |
| Form fields | `Form()` | `python-multipart` |
| Uploaded file | `UploadFile` / `File()` | `python-multipart` |
| Cookie | `Cookie()` | none |
| Header | `Header()` | none |

You already used a form in chapter 11: `OAuth2PasswordRequestForm` reads `username` and `password` from a form.

## Forms

```python
from typing import Annotated
from fastapi import Form

@router.post("/contact")
async def contact(
    name: Annotated[str, Form(min_length=1)],
    message: Annotated[str, Form(max_length=500)],
):
    return {"name": name, "length": len(message)}
```

```bash
curl -X POST localhost:8000/api/v1/contact -d "name=Asha&message=Hello"
# -> {"name":"Asha","length":5}
```

> A route cannot read both a JSON body and form fields. The HTTP request has only one body.

## File uploads

Users upload profile pictures, PDFs for your RAG app, CSV files. Files are dangerous input. Check everything: **type**, **size**, **name**.

`app/api/routes/files.py`:

```python
from pathlib import Path
from typing import Annotated

from fastapi import APIRouter, File, HTTPException, UploadFile

router = APIRouter(prefix="/files", tags=["files"])

UPLOAD_DIR = Path("uploads")
ALLOWED_TYPES = {"image/png", "image/jpeg", "application/pdf"}
MAX_BYTES = 1_000_000


@router.post("")
async def upload(file: Annotated[UploadFile, File()]):
    if file.content_type not in ALLOWED_TYPES:
        raise HTTPException(415, "Only png, jpeg and pdf files are allowed")
    data = await file.read(MAX_BYTES + 1)
    if len(data) > MAX_BYTES:
        raise HTTPException(413, "File is larger than 1 MB")
    UPLOAD_DIR.mkdir(exist_ok=True)
    safe_name = Path(file.filename or "upload").name  # drop any folders from the name
    (UPLOAD_DIR / safe_name).write_bytes(data)
    return {"filename": safe_name, "size": len(data)}
```

Line by line:

- `UploadFile` is a file-like object. FastAPI keeps big files on disk instead of memory.
- `content_type` is what the client **claims**. It can lie. For high-risk apps, also check the file's real content (its first bytes).
- `file.read(MAX_BYTES + 1)` reads at most one byte more than allowed, so we can detect "too big" without loading a huge file.
- `Path(file.filename).name` removes folder parts. A hostile name like `../../etc/passwd` becomes `passwd`. This stops **path traversal** attacks.

```bash
curl -X POST localhost:8000/api/v1/files -F "file=@photo.png"
# -> {"filename":"photo.png","size":24512}
curl -X POST localhost:8000/api/v1/files -F "file=@virus.exe"
# -> {"detail":"Only png, jpeg and pdf files are allowed"}     (415)
```

`-F` sends a multipart form, which is how files travel.

**More than one file:** `files: list[UploadFile]`.

**Where to store files in production:** not on the server's disk. Use object storage (S3), because servers are replaced and you may run several. Save only the **key or URL** in your database.

## Cookies

A cookie is a small value the browser stores and sends back with every request to your site.

**Reading** a cookie:

```python
from fastapi import Cookie

@router.get("/theme")
async def theme(theme: Annotated[str | None, Cookie()] = None):
    return {"theme": theme or "light"}
```

```bash
curl localhost:8000/api/v1/files/theme
# -> {"theme":"light"}
curl localhost:8000/api/v1/files/theme --cookie "theme=dark"
# -> {"theme":"dark"}
```

**Setting** a cookie. Ask for a `Response` object in your function:

```python
from fastapi import Response

@router.post("/theme")
async def set_theme(response: Response):
    response.set_cookie(
        "theme", "dark",
        max_age=3600,        # seconds
        httponly=True,       # JavaScript cannot read it
        secure=True,         # only over HTTPS
        samesite="lax",      # helps against CSRF
    )
    return {"ok": True}
```

The four options are important for any cookie that holds a session or token:

| Option | Protects against |
| --- | --- |
| `httponly=True` | scripts stealing the cookie (XSS) |
| `secure=True` | sending it over plain HTTP |
| `samesite="lax"` | another site making the browser send it (CSRF) |
| `max_age` | cookies living forever |

## Headers

```python
from fastapi import Header

@router.get("/whoami")
async def whoami(
    user_agent: Annotated[str | None, Header()] = None,
    x_request_id: Annotated[str | None, Header()] = None,
):
    return {"agent": user_agent, "request_id": x_request_id}
```

FastAPI changes `x_request_id` to the header name `X-Request-ID` for you (underscores become hyphens).

**Setting** response headers works like cookies: `response.headers["X-Total-Count"] = "42"`.

## Other response types

```python
from fastapi.responses import FileResponse, HTMLResponse, RedirectResponse, PlainTextResponse

@router.get("/download")
async def download():
    return FileResponse("uploads/report.pdf", filename="report.pdf")

@router.get("/old-url")
async def old():
    return RedirectResponse("/api/v1/tasks", status_code=307)

@router.get("/page", response_class=HTMLResponse)
async def page():
    return "<h1>Hello</h1>"
```

## `response_model_exclude_none`

If many optional fields are `None`, you can leave them out of the answer:

```python
@router.get("/{task_id}", response_model=TaskOut, response_model_exclude_none=True)
```

::: {.box .checkpoint}
**Folder now**

```
app/api/routes/
└── files.py        # NEW: upload with checks, a cookie reader
uploads/            # created at runtime (add it to .gitignore)
```

**Checkpoint:** a `png` upload succeeds with its size. An `.exe` upload returns `415`. `?theme` reads `dark` when you send the cookie.
:::

## Common mistakes

::: {.box .mistake}
**Common mistakes**

- Trusting the file name (path traversal) or only the claimed `content_type`.
- Reading the whole upload into memory with no size limit.
- Saving uploads inside your code folder, or serving them from a folder that can run code.
- Storing user files on the server's disk in production.
- Cookies without `httponly`, `secure` and `samesite` for sessions.
- Forgetting to install `python-multipart` (you get a clear error that it is needed).
:::

## Interview corner

::: {.box .interview}
**Interview corner**

**Q: How do you handle file uploads safely?**
Limit the size, check the type (and ideally real content), clean the file name, store outside the code folder or in object storage, and never execute uploaded files.

**Q: Why `python-multipart`?**
It parses `multipart/form-data` and form bodies, which FastAPI needs for `Form` and `File`.

**Q: What do `HttpOnly`, `Secure` and `SameSite` do on a cookie?**
`HttpOnly` hides it from JavaScript, `Secure` sends it only over HTTPS, `SameSite` limits cross-site sending to reduce CSRF.

**Q: Can one route take both JSON and a file?**
Not in the same body. Use multipart fields: a file plus form fields (or JSON sent as a form field).
:::

## Exercises

::: {.box .exercise}
**Exercises**

1. Make the upload route accept only files up to 200 KB and test with a bigger file.
2. Add a route that accepts several files and returns each name and size.
3. Save the uploaded file with a random name (`uuid4().hex`) and return that name. Why is that safer?
4. Set a cookie `visited=1` the first time someone calls `/api/v1/hello`, and return `"welcome back"` the second time.
5. **Think:** why is it a bad idea to trust the `content_type` that the client sends?
:::
