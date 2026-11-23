import json


def validate_tool_args(args_json, required):
    try:
        args = json.loads(args_json)
    except json.JSONDecodeError:
        return False, "invalid JSON"
    if not isinstance(args, dict):
        return False, "arguments must be an object"
    missing = [name for name in required if name not in args]
    if missing:
        return False, "missing: " + ", ".join(missing)
    return True, args
