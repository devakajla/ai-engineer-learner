TRIFECTA = {"private_data", "untrusted_input", "external_comm"}


def capabilities_of(tool_names, table):
    caps = set()
    for name in tool_names:
        caps.update(table.get(name, sorted(TRIFECTA)))  # an unknown tool is assumed to be risky
    return sorted(caps)


def check_trifecta(tool_names, table):
    caps = capabilities_of(tool_names, table)
    return {"caps": caps, "danger": TRIFECTA <= set(caps)}


def break_trifecta(tool_names, table):
    if not check_trifecta(tool_names, table)["danger"]:
        return list(tool_names)
    return [name for name in tool_names if "external_comm" not in table.get(name, sorted(TRIFECTA))]
