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


# Your task:
def handle_request(tools, request):
    ...
