# Log in with a form and a cookie

Browsers send HTML forms as **form data**, not JSON. Create `app` with two routes:

**`POST /login`** takes two **form** fields, `username` and `password`.

- If `username == "dev"` and `password == "secret123"`: answer `{"ok": true}` and set a cookie named `session` with the value `abc123`. The cookie must be **`httponly`**.
- Anything else: **401** with `{"detail": "Wrong username or password"}`, and no cookie.

**`GET /me`** reads the cookie `session`.

- If it is `abc123`: answer `{"user": "dev"}`.
- If the cookie is missing or has another value: **401** with `{"detail": "Not logged in"}`.

```text
POST /login (form: username=dev, password=secret123)  -> 200 {"ok": true}   + Set-Cookie: session=abc123; HttpOnly
GET  /me     (cookie: session=abc123)                  -> 200 {"user": "dev"}
GET  /me     (no cookie)                               -> 401
```

**Think first:** Why must the cookie be `httponly`?

**Hint:** `Form()` and `Cookie()` from `fastapi`. To set a cookie, add a parameter `response: Response` and call `response.set_cookie(key=..., value=..., httponly=True)`.
