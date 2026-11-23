from solution import needs_approval, tool_risk, tools_for_role

TABLE = {"search": "low", "pay": "medium", "delete_file": "high"}
LIMITS = {"pay": {"amount": 100}}


def test_tool_risk_and_unknown_tools_are_high():
    assert tool_risk("search", TABLE) == "low"
    assert tool_risk("pay", TABLE) == "medium"
    assert tool_risk("new_tool", TABLE) == "high", "a tool nobody classified is treated as risky"


def test_low_never_needs_approval_high_always_does():
    assert needs_approval("search", {}, TABLE) is False
    assert needs_approval("delete_file", {}, TABLE) is True
    assert needs_approval("mystery", {}, TABLE) is True


def test_medium_needs_approval_only_over_the_limit():
    assert needs_approval("pay", {"amount": 50}, TABLE, LIMITS) is False
    assert needs_approval("pay", {"amount": 100}, TABLE, LIMITS) is False
    assert needs_approval("pay", {"amount": 101}, TABLE, LIMITS) is True


def test_medium_without_limits_or_missing_argument_does_not_ask():
    assert needs_approval("pay", {"amount": 10_000}, TABLE) is False
    assert needs_approval("pay", {}, TABLE, LIMITS) is False


def test_roles_get_only_their_tools_in_the_original_order():
    roles = {"support": ["search", "pay"], "reader": ["search"]}
    all_tools = ["delete_file", "pay", "search"]
    assert tools_for_role("support", roles, all_tools) == ["pay", "search"]
    assert tools_for_role("reader", roles, all_tools) == ["search"]


def test_unknown_role_gets_nothing_and_unknown_tool_names_are_ignored():
    assert tools_for_role("guest", {"reader": ["search"]}, ["search"]) == []
    assert tools_for_role("reader", {"reader": ["search", "ghost"]}, ["search"]) == ["search"]
