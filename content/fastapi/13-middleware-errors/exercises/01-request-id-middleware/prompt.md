# Request-ID, timing and CORS

Create `app` with:

1. An HTTP middleware that:
   - uses the incoming `X-Request-ID` header if present, otherwise generates `uuid.uuid4().hex`
   - stores it on `request.state.request_id` (so routes can read it)
   - adds `X-Request-ID` and `X-Process-Time-Ms` (a number, e.g. `"3.2"`) to **every** response — including 404s
2. `CORSMiddleware` allowing only `http://localhost:3000`, all methods and headers
3. `GET /whoami` → `{"request_id": request.state.request_id}`

```text
GET /whoami  (X-Request-ID: abc)   -> {"request_id": "abc"}, header X-Request-ID: abc
GET /whoami                        -> generated 32-char hex id in body and header
```
