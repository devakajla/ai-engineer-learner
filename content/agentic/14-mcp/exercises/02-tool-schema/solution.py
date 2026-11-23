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
