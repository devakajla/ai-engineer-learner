from solution import run_with_limits


def test_finishes_inside_the_limits():
    assert run_with_limits([0.01, 0.02, 0.03], max_steps=5, max_cost=1.0) == {"ran": 3, "spent": 0.06, "stopped": "done"}


def test_stops_at_max_steps_before_running_another_step():
    assert run_with_limits([0.01] * 10, max_steps=4, max_cost=1.0) == {"ran": 4, "spent": 0.04, "stopped": "max_steps"}


def test_stops_before_a_step_that_would_break_the_budget():
    out = run_with_limits([0.4, 0.4, 0.4], max_steps=10, max_cost=1.0)
    assert out == {"ran": 2, "spent": 0.8, "stopped": "max_cost"}


def test_exactly_on_the_budget_is_allowed():
    assert run_with_limits([0.5, 0.5], max_steps=10, max_cost=1.0) == {"ran": 2, "spent": 1.0, "stopped": "done"}


def test_no_steps():
    assert run_with_limits([], max_steps=3, max_cost=1.0) == {"ran": 0, "spent": 0.0, "stopped": "done"}


def test_the_first_step_alone_can_be_too_expensive():
    assert run_with_limits([2.0], max_steps=3, max_cost=1.0) == {"ran": 0, "spent": 0.0, "stopped": "max_cost"}


def test_max_steps_is_checked_only_when_another_step_waits():
    assert run_with_limits([0.1, 0.1], max_steps=2, max_cost=1.0)["stopped"] == "done"
