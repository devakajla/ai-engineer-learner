# Interview task: URL shortener API (25 min)

Build an in-memory URL shortener:

| Endpoint | Behaviour |
|---|---|
| `POST /links` body `{"url": "https://..."}` | **201** `{"code": str, "url": str}`. `url` must start with `http://` or `https://` (else 422). **Idempotent**: shortening the same URL again returns the **same code** (status 200 the second time). |
| `GET /{code}` | **307** redirect with `Location: <url>`, and increments a hit counter; unknown code → **404** `{"detail": "Link not found"}` |
| `GET /links/{code}/stats` | `{"code", "url", "hits"}` or 404 |

Codes: **base62** (`0-9a-zA-Z`) encoding of an increasing integer id starting at 1 (id 1 → `"1"`, id 62 → `"10"`). Write `encode_base62(n)` as a separate function.

Be ready to discuss: how would this scale (DB table + unique index on url, cache hot codes, 301 vs 307)?
