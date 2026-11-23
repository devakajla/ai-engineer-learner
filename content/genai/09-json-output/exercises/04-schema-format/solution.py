def schema_format(name, fields):
    properties = {}
    required = []
    for key, type_name in fields.items():
        properties[key] = {"type": type_name}
        required.append(key)
    return {
        "type": "json_schema",
        "json_schema": {
            "name": name,
            "schema": {
                "type": "object",
                "properties": properties,
                "required": required,
                "additionalProperties": False,
            },
        },
    }
