# Given from earlier exercises. Do not change these.
def make_request(request_id, method, params=None):
    message = {"jsonrpc": "2.0", "id": request_id, "method": method}
    if params is not None:
        message["params"] = params
    return message


def make_notification(method, params=None):
    message = {"jsonrpc": "2.0", "method": method}
    if params is not None:
        message["params"] = params
    return message


def make_result(request_id, result):
    return {"jsonrpc": "2.0", "id": request_id, "result": result}


def make_error(request_id, code, message):
    return {"jsonrpc": "2.0", "id": request_id, "error": {"code": code, "message": message}}


def classify(message):
    if "method" in message:
        return "request" if "id" in message else "notification"
    if "result" in message:
        return "result"
    if "error" in message:
        return "error"
    return "invalid"


TYPES = {"int": "integer", "str": "string", "float": "number", "bool": "boolean"}


def to_input_schema(params):
    properties = {}
    for name, type_name in params.items():
        if type_name not in TYPES:
            raise ValueError(f"unknown type: {type_name}")
        properties[name] = {"type": TYPES[type_name]}
    return {"type": "object", "properties": properties, "required": list(params)}


def to_openai_tool(tool):
    return {
        "type": "function",
        "function": {
            "name": tool["name"],
            "description": tool["description"],
            "parameters": tool["inputSchema"],
        },
    }


def result_text(result):
    parts = [item["text"] for item in result.get("content", []) if item.get("type") == "text"]
    return "\n".join(parts)


def handle_request(tools, request):
    if "id" not in request:
        return None  # a notification gets no reply
    request_id = request["id"]
    method = request.get("method")
    params = request.get("params") or {}
    if method == "initialize":
        return make_result(request_id, {
            "protocolVersion": params.get("protocolVersion", "2025-06-18"),
            "capabilities": {"tools": {}},
            "serverInfo": {"name": "demo", "version": "1.0"},
        })
    if method == "tools/list":
        listing = [
            {"name": name, "description": tool["description"], "inputSchema": to_input_schema(tool["params"])}
            for name, tool in tools.items()
        ]
        return make_result(request_id, {"tools": listing})
    if method == "tools/call":
        name = params.get("name")
        if name not in tools:
            return make_error(request_id, -32602, f"Unknown tool: {name}")
        try:
            value = tools[name]["func"](**params.get("arguments", {}))
        except Exception as error:
            return make_result(request_id, {"content": [{"type": "text", "text": f"Error: {error}"}], "isError": True})
        return make_result(request_id, {"content": [{"type": "text", "text": str(value)}], "isError": False})
    return make_error(request_id, -32601, f"Method not found: {method}")


# Your task:
def connect(send):
    ...


def call_tool(send, request_id, name, arguments):
    ...
