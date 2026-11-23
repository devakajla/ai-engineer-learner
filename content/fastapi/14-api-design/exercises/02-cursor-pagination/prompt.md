# Cursor pagination

`EVENTS` (given) has 95 events with increasing `id`s. Implement a newest-first feed:

`GET /events?limit=20&cursor=<opaque>` → `{"items": [...], "next_cursor": str | null}`

- Items are ordered by `id` **descending**.
- The cursor encodes the last returned `id`: `base64.urlsafe_b64encode(json.dumps({"id": 75}).encode()).decode()`. Clients must treat it as opaque.
- With a cursor, return events with `id < cursor_id`.
- `next_cursor` is `null` when there are no more items.
- `limit` 1–50 (default 20). An invalid cursor → **400** `{"detail": "Invalid cursor"}`.

Walking all pages must return every event exactly once — even if new events are appended while paging (the tests do that!).
