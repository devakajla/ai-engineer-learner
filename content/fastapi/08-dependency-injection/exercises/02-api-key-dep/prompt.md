# Protect a router with an API key

Write a dependency `require_api_key` that reads the **`X-API-Key`** header and raises **401** `{"detail": "Invalid API key"}` unless it equals `get_settings().api_key`.

- `get_settings()` returns `Settings()` and is cached with `@lru_cache` (`Settings` is given: `api_key: str = "dev-key"`).
- Create `admin = APIRouter(prefix="/admin", dependencies=[Depends(require_api_key)])` with `GET /admin/stats` → `{"tasks": 42}`.
- A public route `GET /public` → `{"ok": true}` needs no key.

```text
GET /admin/stats                         -> 401
GET /admin/stats  X-API-Key: dev-key     -> 200 {"tasks": 42}
GET /public                              -> 200
```

The tests override `get_settings` to use a different key — so read the key **through the dependency**, not a global.
