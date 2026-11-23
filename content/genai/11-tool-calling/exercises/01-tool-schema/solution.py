def make_tool(name, description, params):
    properties = {}
    for param, (kind, text) in params.items():
        properties[param] = {"type": kind, "description": text}
    return {
        "type": "function",
        "function": {
            "name": name,
            "description": description,
            "parameters": {
                "type": "object",
                "properties": properties,
                "required": list(params),
            },
        },
    }
