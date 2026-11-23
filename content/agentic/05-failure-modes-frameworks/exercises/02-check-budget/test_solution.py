from solution import check_budget


def test_under_every_limit():
    assert check_budget({"steps": 3, "tokens": 900}, {"max_steps": 5, "max_tokens": 1000}) is None


def test_exactly_at_the_limit_counts():
    assert check_budget({"steps": 5}, {"max_steps": 5}) == "max_steps"
    assert check_budget({"tokens": 1000}, {"max_tokens": 1000}) == "max_tokens"


def test_each_limit():
    assert check_budget({"cost": 0.2}, {"max_cost": 0.1}) == "max_cost"
    assert check_budget({"seconds": 31}, {"max_seconds": 30}) == "max_seconds"


def test_no_limits():
    assert check_budget({"steps": 999, "cost": 99}, {}) is None


def test_missing_used_counts_as_zero():
    assert check_budget({}, {"max_steps": 5, "max_cost": 1.0}) is None
    assert check_budget({}, {"max_steps": 0}) == "max_steps"


def test_first_reached_limit_in_fixed_order():
    used = {"steps": 9, "tokens": 9, "cost": 9, "seconds": 9}
    limits = {"max_seconds": 1, "max_cost": 1, "max_tokens": 1, "max_steps": 1}
    assert check_budget(used, limits) == "max_steps"
    assert check_budget(used, {"max_seconds": 1, "max_cost": 1, "max_tokens": 1}) == "max_tokens"
    assert check_budget(used, {"max_seconds": 1, "max_cost": 1}) == "max_cost"


def test_inputs_are_not_changed():
    used, limits = {"steps": 1}, {"max_steps": 5}
    check_budget(used, limits)
    assert used == {"steps": 1} and limits == {"max_steps": 5}
