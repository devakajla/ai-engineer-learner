# One path, three methods

Create `app` with three routes on the **same path** `/items`:

| Request | Response body |
|---|---|
| `GET /items` | `[]` |
| `POST /items` | `{"created": true}` |
| `DELETE /items` | `{"deleted": 0}` |

Any other method on `/items` (e.g. `PUT`) must give **405** — FastAPI does that automatically if you don't add a route for it.
