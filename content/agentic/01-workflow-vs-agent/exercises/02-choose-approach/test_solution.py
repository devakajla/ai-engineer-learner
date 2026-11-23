from solution import choose_approach


def test_no_tools_is_a_single_call():
    assert choose_approach(True, False) == "single_call"
    assert choose_approach(False, False) == "single_call"
    assert choose_approach(False, False, True) == "single_call"


def test_known_steps_is_a_workflow():
    assert choose_approach(True, True) == "workflow"
    assert choose_approach(True, True, True) == "workflow", "known steps win over risk"


def test_unknown_steps_is_an_agent():
    assert choose_approach(False, True) == "agent"
    assert choose_approach(steps_known=False, needs_tools=True, high_risk=False) == "agent"


def test_risky_agent_needs_approval():
    assert choose_approach(False, True, True) == "agent_with_approval"
    assert choose_approach(steps_known=False, needs_tools=True, high_risk=True) == "agent_with_approval"
