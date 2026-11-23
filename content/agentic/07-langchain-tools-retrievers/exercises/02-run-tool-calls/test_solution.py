from langchain_core.messages import AIMessage, ToolMessage
from langchain_core.tools import tool

from solution import convert_temp, run_tool_calls


@tool
def fail(x: int) -> int:
    """Always fails."""
    raise ValueError("bad input")


def ai(*calls):
    return AIMessage(content="", tool_calls=[{"name": n, "args": a, "id": i} for n, a, i in calls])


def test_runs_one_call():
    out = run_tool_calls(ai(("convert_temp", {"celsius": 100}, "c1")), [convert_temp])
    assert len(out) == 1 and isinstance(out[0], ToolMessage)
    assert out[0].content == "212.0", "the content is the result as a string"
    assert out[0].tool_call_id == "c1", "the id must match the call, so the model can pair them"


def test_runs_many_calls_in_order():
    out = run_tool_calls(
        ai(("convert_temp", {"celsius": 0}, "a"), ("convert_temp", {"celsius": 100}, "b")), [convert_temp]
    )
    assert [(m.tool_call_id, m.content) for m in out] == [("a", "32.0"), ("b", "212.0")]


def test_no_calls_gives_empty_list():
    assert run_tool_calls(AIMessage(content="hello"), [convert_temp]) == []


def test_unknown_tool_is_an_error_message_not_a_crash():
    out = run_tool_calls(ai(("teleport", {}, "z")), [convert_temp])
    assert out[0].content == "Error: unknown tool teleport" and out[0].tool_call_id == "z"


def test_tool_error_becomes_a_message():
    out = run_tool_calls(ai(("fail", {"x": 1}, "f1"), ("convert_temp", {"celsius": 0}, "f2")), [fail, convert_temp])
    assert out[0].content == "Error: bad input", "the model should see the error and can try again"
    assert out[1].content == "32.0", "one failing call must not stop the others"
