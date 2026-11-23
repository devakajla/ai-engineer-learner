# A small app with a sub-app, compression and host check

Create `app` with:

- `GET /small` → `{"ok": true}`
- `GET /big` → `{"data": "x" * 2000}`
- a second FastAPI app `admin` with `GET /stats` → `{"admin": true}`, **mounted** at `/admin` (so the URL is `/admin/stats`)
- **GZip** compression for answers of **1000 bytes or more**
- a **trusted host** check that allows only the hosts `testserver` and `api.example.com`. Other `Host` headers get **400**.

```text
GET /small  (Accept-Encoding: gzip)  -> 200, no Content-Encoding header (too small)
GET /big    (Accept-Encoding: gzip)  -> 200, Content-Encoding: gzip
GET /admin/stats                     -> {"admin": true}
GET /small  (Host: evil.com)         -> 400
```

**Think first:** Why does compressing a 20-byte answer waste time?

**Hint:** `app.add_middleware(GZipMiddleware, minimum_size=1000)`, `app.add_middleware(TrustedHostMiddleware, allowed_hosts=[...])`, `app.mount("/admin", admin)`. Imports are in `fastapi.middleware.gzip` and `fastapi.middleware.trustedhost`.
