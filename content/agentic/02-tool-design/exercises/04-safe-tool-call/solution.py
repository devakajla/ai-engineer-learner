# Given from earlier exercises. Do not change these.
def type_ok(kind, value):
    if kind == "string":
        return isinstance(value, str)
    if kind == "integer":
        return isinstance(value, int) and not isinstance(value, bool)
    if kind == "number":
        return isinstance(value, (int, float)) and not isinstance(value, bool)
    if kind == "boolean":
        return isinstance(value, bool)
    if kind == "array":
        return isinstance(value, list)
    if kind == "object":
        return isinstance(value, dict)
    return True


def validate_args(tool, args):
    parameters = tool["function"].get("parameters", {})
    properties = parameters.get("properties", {})
    problems = []
    for required in parameters.get("required", []):
        if required not in args:
            problems.append(f"missing required argument {required}")
    for name, value in args.items():
        if name not in properties:
            problems.append(f"unknown argument {name}")
        elif not type_ok(properties[name].get("type"), value):
            problems.append(f"argument {name} must be {properties[name]['type']}")
    return problems


def truncate_result(text, max_chars):
    if len(text) <= max_chars:
        return text
    more = len(text) - max_chars
    return text[:max_chars] + f"\n[truncated {more} more characters]"


def safe_tool_call(tools, functions, name, args, max_chars=500):
    tool = None
    for candidate in tools:
        if candidate["function"]["name"] == name:
            tool = candidate
    if tool is None or name not in functions:
        names = sorted(candidate["function"]["name"] for candidate in tools)
        available = ", ".join(names) if names else "(none)"
        return f"error: unknown tool {name}. Available tools: {available}"
    problems = validate_args(tool, args)
    if problems:
        return "error: " + "; ".join(problems)
    try:
        result = functions[name](**args)
    except Exception as error:
        return f"error: {type(error).__name__}: {error}"
    return truncate_result(str(result), max_chars)
