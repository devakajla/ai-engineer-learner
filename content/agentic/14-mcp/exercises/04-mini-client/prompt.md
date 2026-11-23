# A tiny MCP client

The client side of MCP has two jobs. First the **handshake**: say hello, tell the server you are ready, ask for its tools. Then **calls**: send `tools/call` and read the answer. The client gets a function `send(message)` that delivers one message and returns the reply (in real life it talks over stdio or HTTP; in your tests it calls `handle_request` directly).

The starter gives you the message helpers, the schema helpers and the server's `handle_request`. Write:

1. `connect(send)`:
   - `send(make_request(1, "initialize", {"protocolVersion": "2025-06-18", "clientInfo": {"name": "mini"}}))`. If the reply has an `"error"`, raise `RuntimeError(error["message"])`.
   - `send(make_notification("notifications/initialized"))` (you ignore the reply).
   - `send(make_request(2, "tools/list"))`. If it is an error, raise the same way.
   - Return `[to_openai_tool(tool) for tool in reply["result"]["tools"]]`, the tools ready to give to a chat model.
2. `call_tool(send, request_id, name, arguments)`: send a `"tools/call"` request with `{"name": name, "arguments": arguments}`. A protocol `"error"` raises `RuntimeError(error["message"])`. Otherwise return `result_text(reply["result"])`. (A tool that failed returns its error text as normal text. The model reads it and can try again.)

```python
tools = connect(send)            # list of {"type": "function", "function": {...}}
call_tool(send, 7, "add", {"a": 2, "b": 5})
# -> '7'
```

**Think first:** why does `call_tool` raise on a protocol error but return text when a tool fails?

**Hint:** the handshake order matters: initialize, then the `initialized` notification, then everything else.
