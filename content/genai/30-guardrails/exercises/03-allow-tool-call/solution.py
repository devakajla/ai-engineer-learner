def allow_tool_call(name, args, allowed, risky, approve):
    if name not in allowed:
        return {"ok": False, "reason": "tool not allowed"}
    if name in risky:
        if not approve(name, args):
            return {"ok": False, "reason": "not approved"}
    return {"ok": True, "reason": ""}
