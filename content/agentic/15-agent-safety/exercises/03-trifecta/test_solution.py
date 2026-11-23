from solution import break_trifecta, capabilities_of, check_trifecta

TABLE = {
    "read_email": ["private_data", "untrusted_input"],
    "web_search": ["untrusted_input"],
    "send_email": ["external_comm"],
    "calc": [],
}


def test_capabilities_are_merged_and_sorted():
    assert capabilities_of(["read_email", "send_email"], TABLE) == ["external_comm", "private_data", "untrusted_input"]
    assert capabilities_of(["calc"], TABLE) == []
    assert capabilities_of([], TABLE) == []


def test_unknown_tool_is_assumed_to_have_every_capability():
    assert capabilities_of(["mystery"], TABLE) == ["external_comm", "private_data", "untrusted_input"]


def test_check_trifecta_needs_all_three():
    assert check_trifecta(["read_email", "send_email"], TABLE) == {
        "caps": ["external_comm", "private_data", "untrusted_input"], "danger": True}
    assert check_trifecta(["web_search", "send_email"], TABLE)["danger"] is False
    assert check_trifecta(["read_email"], TABLE)["danger"] is False
    assert check_trifecta(["web_search", "read_email", "send_email"], TABLE)["danger"] is True


def test_break_trifecta_drops_the_outgoing_tools_only_when_dangerous():
    names = ["read_email", "web_search", "send_email", "calc"]
    assert break_trifecta(names, TABLE) == ["read_email", "web_search", "calc"]


def test_safe_sets_are_returned_unchanged_and_as_a_copy():
    names = ["web_search", "send_email"]
    out = break_trifecta(names, TABLE)
    assert out == names and out is not names


def test_unknown_tool_is_dropped_when_the_set_is_dangerous():
    assert break_trifecta(["read_email", "web_search", "mystery"], TABLE) == ["read_email", "web_search"]
