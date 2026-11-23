from solution import pick_by_numbers

OPTIONS = [
    {"name": "single", "success": 0.70, "cost": 0.001, "seconds": 1},
    {"name": "workflow", "success": 0.90, "cost": 0.004, "seconds": 4},
    {"name": "agent", "success": 0.95, "cost": 0.030, "seconds": 20},
]


def test_cheapest_good_one():
    assert pick_by_numbers(OPTIONS, 0.85, 0.05, 30) == "workflow"
    assert pick_by_numbers(OPTIONS, 0.5, 0.05, 30) == "single"


def test_nothing_good_enough():
    assert pick_by_numbers(OPTIONS, 0.99, 0.05, 30) is None
    assert pick_by_numbers([], 0.5, 1, 1) is None


def test_limits_are_inclusive():
    assert pick_by_numbers(OPTIONS, 0.95, 0.03, 20) == "agent"


def test_cost_and_time_limits_remove_candidates():
    assert pick_by_numbers(OPTIONS, 0.9, 0.01, 30) == "workflow"
    assert pick_by_numbers(OPTIONS, 0.95, 0.05, 10) is None


def test_ties_go_to_the_faster_then_the_name():
    tied = [
        {"name": "b", "success": 1, "cost": 0.01, "seconds": 5},
        {"name": "a", "success": 1, "cost": 0.01, "seconds": 5},
        {"name": "fast", "success": 1, "cost": 0.01, "seconds": 2},
    ]
    assert pick_by_numbers(tied, 0.5, 1, 10) == "fast"
    assert pick_by_numbers(tied[:2], 0.5, 1, 10) == "a"


def test_input_is_not_changed():
    before = [dict(c) for c in OPTIONS]
    pick_by_numbers(OPTIONS, 0.5, 1, 100)
    assert OPTIONS == before
