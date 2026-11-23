from solution import build_router_graph, classify, pick_route


def test_classify_looks_for_digits():
    assert classify({"question": "what is 2+2", "route": "", "answer": ""}) == {"route": "math"}
    assert classify({"question": "hello there", "route": "", "answer": ""}) == {"route": "chat"}


def test_pick_route_reads_the_state():
    assert pick_route({"route": "math"}) == "math"
    assert pick_route({"route": "chat"}) == "chat"


def test_math_question_goes_to_the_math_node():
    app = build_router_graph()
    out = app.invoke({"question": "7 times 8", "route": "", "answer": ""})
    assert out["route"] == "math" and out["answer"] == "math handler: 7 times 8"


def test_other_question_goes_to_the_chat_node():
    app = build_router_graph()
    out = app.invoke({"question": "tell me a joke", "route": "", "answer": ""})
    assert out["route"] == "chat" and out["answer"] == "chat handler: tell me a joke"


def test_only_one_branch_runs():
    app = build_router_graph()
    seen = [list(u)[0] for u in app.stream({"question": "1+1", "route": "", "answer": ""}, stream_mode="updates")]
    assert seen == ["classify", "math"], "the chat node must not run for a math question"
