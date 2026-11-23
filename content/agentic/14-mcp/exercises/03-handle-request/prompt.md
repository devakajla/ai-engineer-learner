# A tiny MCP server (the heart of it)

An MCP server is a loop: **read a message, answer it**. The answering part is one function. It looks at the `method` and replies. You build it without any MCP library, so you see exactly what a library hides.

The starter gives you the message helpers (exercise 1) and `to_input_schema` (exercise 2). A **tools** table describes the server's tools:

```python
tools = {"add": {"description": "Add two numbers.", "params": {"a": "int", "b": "int"}, "func": add}}
```

Write `handle_request(tools, request)`. It returns the reply message, or `None`:

- No `"id"` in the request (a notification): return `None`.
- `"initialize"`: `make_result(id, {"protocolVersion": <the client's params["protocolVersion"], default "2025-06-18">, "capabilities": {"tools": {}}, "serverInfo": {"name": "demo", "version": "1.0"}})`.
- `"tools/list"`: `make_result(id, {"tools": [{"name", "description", "inputSchema": to_input_schema(tool["params"])}, ...]})` in the table's order.
- `"tools/call"` with `params = {"name": ..., "arguments": {...}}`:
  - unknown name: `make_error(id, -32602, f"Unknown tool: {name}")`.
  - call `tool["func"](**arguments)`. Success: `make_result(id, {"content": [{"type": "text", "text": str(value)}], "isError": False})`.
  - if the tool raises: **not** a protocol error. Return a normal result with `"text": f"Error: {error}"` and `"isError": True`. The model can read this and try again.
- any other method: `make_error(id, -32601, f"Method not found: {method}")`.

```python
handle_request(tools, make_request(3, "tools/call", {"name": "add", "arguments": {"a": 2, "b": 3}}))
# -> {'jsonrpc': '2.0', 'id': 3, 'result': {'content': [{'type': 'text', 'text': '5'}], 'isError': False}}
```

**Think first:** why is a crashing tool a *result* and an unknown method an *error*?

**Hint:** `params = request.get("params") or {}` makes a missing `params` safe.
