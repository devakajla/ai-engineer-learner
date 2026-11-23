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
