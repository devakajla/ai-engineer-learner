from solution import allow_tool_call


class Approver:
    def __init__(self, answer):
        self.answer = answer
        self.asked = []

    def __call__(self, name, args):
        self.asked.append((name, args))
        return self.answer


def test_safe_tool_needs_no_approval():
    approve = Approver(False)
    out = allow_tool_call("search", {}, ["search", "refund"], ["refund"], approve)
    assert out == {"ok": True, "reason": ""} and approve.asked == []


def test_risky_tool_is_asked():
    approve = Approver(True)
    out = allow_tool_call("refund", {"id": 7}, ["search", "refund"], ["refund"], approve)
    assert out == {"ok": True, "reason": ""}
    assert approve.asked == [("refund", {"id": 7})]


def test_risky_tool_refused():
    out = allow_tool_call("refund", {"id": 7}, ["refund"], ["refund"], Approver(False))
    assert out == {"ok": False, "reason": "not approved"}


def test_unknown_tool_never_asks():
    approve = Approver(True)
    out = allow_tool_call("drop_db", {}, ["search"], [], approve)
    assert out == {"ok": False, "reason": "tool not allowed"} and approve.asked == []


def test_risky_but_not_allowed():
    approve = Approver(True)
    out = allow_tool_call("refund", {}, ["search"], ["refund"], approve)
    assert out["reason"] == "tool not allowed" and approve.asked == []
