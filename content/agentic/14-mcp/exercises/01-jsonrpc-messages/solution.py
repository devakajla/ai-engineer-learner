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
