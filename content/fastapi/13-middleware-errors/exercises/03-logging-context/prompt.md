# Request IDs in every log line

Write:

- `request_id_var: ContextVar[str]` (default `"-"`)
- `class RequestIdFilter(logging.Filter)` that sets `record.request_id = request_id_var.get()` and returns `True`
- `logger = logging.getLogger("notes")` with the filter **added to the logger** (`logger.addFilter(...)`)
- a middleware that sets `request_id_var` from `X-Request-ID` (or a new uuid hex), logs **one INFO line** per request: `"%s %s -> %s"` with method, path, status code, and returns the id in the `X-Request-ID` header
- `GET /notes` that logs `INFO "listing notes"` and returns `[]`

The tests capture logs and check every record from this request has the same `request_id` as the response header.
