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
