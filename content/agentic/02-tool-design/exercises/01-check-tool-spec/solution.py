import string

TYPES = ["string", "integer", "number", "boolean", "array", "object"]


def check_tool_spec(tool):
    function = tool["function"]
    problems = []
    name = function.get("name", "")
    allowed = string.ascii_lowercase + string.digits + "_"
    if not name or any(char not in allowed for char in name):
        problems.append("name must use lowercase letters, digits and underscores only")
    if len(function.get("description", "").strip()) < 20:
        problems.append("description is too short (under 20 characters)")
    parameters = function.get("parameters", {})
    properties = parameters.get("properties", {})
    for param, info in properties.items():
        if not info.get("description", "").strip():
            problems.append(f"parameter {param} has no description")
        if info.get("type") not in TYPES:
            problems.append(f"parameter {param} has an unknown type")
    for required in parameters.get("required", []):
        if required not in properties:
            problems.append(f"required parameter {required} is not in properties")
    return problems
