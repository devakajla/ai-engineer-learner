from solution import answer_request, ask_human, build_approval_graph, choose, start_request


def test_choose():
    assert choose({"approved": True}) == "run"
    assert choose({"approved": False}) == "cancel"


def test_run_pauses_and_returns_the_question():
    app = build_approval_graph()
    question = start_request(app, "t1", "pay 100")
    assert question == "Approve: pay 100?"
    state = app.get_state({"configurable": {"thread_id": "t1"}})
    assert state.next == ("ask_human",), "the graph must wait at the human node"
    assert state.values["result"] == "", "nothing ran yet"


def test_yes_runs_the_action():
    app = build_approval_graph()
    start_request(app, "t1", "pay 100")
    out = answer_request(app, "t1", "yes")
    assert out["approved"] is True and out["result"] == "done: pay 100"


def test_anything_else_cancels():
    app = build_approval_graph()
    start_request(app, "t1", "delete all")
    assert answer_request(app, "t1", "no")["result"] == "cancelled: delete all"
    start_request(app, "t2", "delete all")
    assert answer_request(app, "t2", "maybe")["result"] == "cancelled: delete all"


def test_two_threads_wait_independently():
    app = build_approval_graph()
    start_request(app, "a", "one")
    start_request(app, "b", "two")
    assert answer_request(app, "b", "yes")["result"] == "done: two"
    assert answer_request(app, "a", "no")["result"] == "cancelled: one"
