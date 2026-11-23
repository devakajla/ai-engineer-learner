from langgraph.types import Command

from solution import apply_review, build_review_graph

CFG = {"configurable": {"thread_id": "r"}}


def test_apply_review_approve_keeps_the_draft():
    assert apply_review("Dear Sam", {"action": "approve"}) == "Dear Sam"


def test_apply_review_edit_uses_the_new_text():
    assert apply_review("Dear Sam", {"action": "edit", "text": "Hello Sam"}) == "Hello Sam"


def test_apply_review_edit_without_text_keeps_the_draft():
    assert apply_review("Dear Sam", {"action": "edit"}) == "Dear Sam"


def test_apply_review_reject_and_unknown_give_none():
    assert apply_review("Dear Sam", {"action": "reject"}) is None
    assert apply_review("Dear Sam", {"action": "banana"}) is None
    assert apply_review("Dear Sam", {}) is None


def test_graph_pauses_with_the_draft_and_the_options():
    app = build_review_graph()
    out = app.invoke({"draft": "Dear Sam", "final": ""}, CFG)
    payload = out["__interrupt__"][0].value
    assert payload == {"draft": "Dear Sam", "options": ["approve", "edit", "reject"]}


def test_graph_resumes_with_each_kind_of_review():
    for review, expected in [
        ({"action": "approve"}, "Dear Sam"),
        ({"action": "edit", "text": "Hi Sam"}, "Hi Sam"),
        ({"action": "reject"}, "REJECTED"),
    ]:
        app = build_review_graph()
        app.invoke({"draft": "Dear Sam", "final": ""}, CFG)
        assert app.invoke(Command(resume=review), CFG)["final"] == expected
