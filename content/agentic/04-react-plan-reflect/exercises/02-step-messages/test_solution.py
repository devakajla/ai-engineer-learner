from solution import build_step_messages


def test_roles_and_system_text():
    msgs = build_step_messages("G", ["a", "b"], [], 0)
    assert [m["role"] for m in msgs] == ["system", "user"]
    assert msgs[0]["content"] == "You are carrying out one step of a plan. Do only the current step."


def test_first_step():
    user = build_step_messages("Boil an egg", ["Fill a pot", "Boil it"], [], 0)[1]["content"]
    assert user == (
        "Goal: Boil an egg\n\nPlan:\n1. Fill a pot\n2. Boil it\n\n"
        "Results so far:\n(none yet)\n\nCurrent step (1 of 2): Fill a pot"
    )


def test_second_step_shows_earlier_results():
    user = build_step_messages("Boil an egg", ["Fill a pot", "Boil it"], ["done"], 1)[1]["content"]
    assert user == (
        "Goal: Boil an egg\n\nPlan:\n1. Fill a pot\n2. Boil it\n\n"
        "Results so far:\n1. done\n\nCurrent step (2 of 2): Boil it"
    )


def test_only_finished_results_are_shown():
    user = build_step_messages("G", ["a", "b", "c"], ["r1", "r2", "r3"], 1)[1]["content"]
    assert "1. r1" in user and "r2" not in user and "r3" not in user


def test_three_results():
    user = build_step_messages("G", ["a", "b", "c", "d"], ["r1", "r2", "r3"], 3)[1]["content"]
    assert "Results so far:\n1. r1\n2. r2\n3. r3\n\nCurrent step (4 of 4): d" in user


def test_inputs_are_not_changed():
    steps, results = ["a", "b"], ["r"]
    build_step_messages("G", steps, results, 1)
    assert steps == ["a", "b"] and results == ["r"]
