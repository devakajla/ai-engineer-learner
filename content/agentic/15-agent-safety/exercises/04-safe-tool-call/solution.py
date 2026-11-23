# Given from earlier exercises. Do not change these.
PATTERNS = {
    "override": ["ignore previous", "ignore all previous", "disregard"],
    "secret": ["system prompt", "api key", "password"],
    "hidden": ["do not tell the user", "don't tell the user"],
    "exfil": ["send it to", "send this to", "upload it to"],
}


def scan_tool_output(text):
    lower = text.lower()
    return sorted(label for label, phrases in PATTERNS.items() if any(p in lower for p in phrases))


def quarantine(name, text, max_chars=300):
    flags = scan_tool_output(text)
    body = text if len(text) <= max_chars else text[:max_chars] + "...[cut]"
    body = body.replace("</tool_output>", "[tag removed]")
    wrapped = f'<tool_output name="{name}" trust="untrusted">\n{body}\n</tool_output>'
    return {"text": wrapped, "flags": flags}


def tool_risk(name, table):
    return table.get(name, "high")


def needs_approval(name, args, table, limits=None):
    risk = tool_risk(name, table)
    if risk == "high":
        return True
    if risk == "medium":
        for key, limit in (limits or {}).get(name, {}).items():
            if args.get(key, 0) > limit:
                return True
    return False


def tools_for_role(role, roles, all_tools):
    allowed = roles.get(role, [])
    return [tool for tool in all_tools if tool in allowed]


# Your task:
def run_tool_safely(call, registry, table, approve, audit, limits=None):
    name = call["name"]
    args = call.get("args", {})
    if name not in registry:
        audit.append({"tool": name, "args": args, "decision": "unknown", "flags": []})
        return f"Error: unknown tool {name}"
    decision = "ran"
    if needs_approval(name, args, table, limits):
        if not approve(name, args):
            audit.append({"tool": name, "args": args, "decision": "denied", "flags": []})
            return "DENIED: a person did not approve this call"
        decision = "approved"
    try:
        raw = str(registry[name](**args))
    except Exception as error:
        raw = f"Error: {error}"
    result = quarantine(name, raw)
    audit.append({"tool": name, "args": args, "decision": decision, "flags": result["flags"]})
    return result["text"]
