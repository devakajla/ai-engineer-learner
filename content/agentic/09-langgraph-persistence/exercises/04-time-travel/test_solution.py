from solution import build_counter, fork_from, list_checkpoints, replay_from

CFG = {"configurable": {"thread_id": "t"}}


def run_once():
    app = build_counter()
    app.invoke({"n": 1, "log": []}, CFG)
    return app


def test_list_checkpoints_oldest_first():
    cps = list_checkpoints(run_once(), "t")
    assert [c["step"] for c in cps] == [-1, 0, 1, 2]
    assert cps[0]["next"] == ["__start__"]
    assert cps[1]["next"] == ["inc"] and cps[1]["values"]["n"] == 1
    assert cps[-1]["next"] == [] and cps[-1]["values"] == {"n": 4, "log": ["inc", "double"]}


def test_replay_from_a_step_runs_the_rest_again():
    app = run_once()
    assert replay_from(app, "t", 1) == {"n": 4, "log": ["inc", "double"]}, "from step 1 only `double` runs again"
    assert replay_from(app, "t", 0) == {"n": 4, "log": ["inc", "double"]}, "from step 0 both nodes run again"


def test_fork_changes_the_state_and_runs_forward():
    app = run_once()
    out = fork_from(app, "t", 1, {"n": 10})
    assert out == {"n": 20, "log": ["inc", "double"]}, "step 1 had n=2; we set n=10; `double` then makes 20"


def test_fork_on_a_fresh_thread_leaves_the_original_result_unchanged():
    app = run_once()
    fork_from(app, "t", 1, {"n": 10})
    other = {"configurable": {"thread_id": "other"}}
    assert app.invoke({"n": 1, "log": []}, other)["n"] == 4, "other threads are not touched"


def test_find_checkpoint_unknown_step_is_none():
    from solution import find_checkpoint

    assert find_checkpoint(run_once(), "t", 99) is None
