# The messages MCP speaks

**MCP** (Model Context Protocol) is a standard way for an AI app (the **client**) to use tools and data from another program (the **server**). Under the hood it sends small JSON messages in a format called **JSON-RPC 2.0**. Four kinds of message:

| Kind | Looks like |
|---|---|
| request | `{"jsonrpc": "2.0", "id": 1, "method": "tools/list"}` (has an `id`, wants an answer) |
| notification | `{"jsonrpc": "2.0", "method": "notifications/initialized"}` (no `id`, no answer) |
| result | `{"jsonrpc": "2.0", "id": 1, "result": {...}}` |
| error | `{"jsonrpc": "2.0", "id": 1, "error": {"code": -32601, "message": "..."}}` |

Write five small functions that build and recognise them (plain dicts, no libraries):

1. `make_request(request_id, method, params=None)`: keys `jsonrpc` (`"2.0"`), `id`, `method`, and `params` **only if** `params` is not `None`.
2. `make_notification(method, params=None)`: like a request, but **no** `id`.
3. `make_result(request_id, result)` and 4. `make_error(request_id, code, message)` (the error has a dict `{"code": ..., "message": ...}` under `"error"`).
5. `classify(message)`: return `"request"` if it has `"method"` and `"id"`, `"notification"` if it has `"method"` but no `"id"`, `"result"` if it has `"result"`, `"error"` if it has `"error"`, otherwise `"invalid"`.

```python
make_request(1, "tools/list")
# -> {'jsonrpc': '2.0', 'id': 1, 'method': 'tools/list'}
classify(make_notification("notifications/initialized"))
# -> 'notification'
```

**Think first:** why does a request carry an `id`?

**Hint:** test `"id" in message`, not `message.get("id")`. An id of `0` is valid but false-looking.
