from types import SimpleNamespace as NS

from solution import run_tool_call


def make_call(name, arguments, call_id="c1"):
    return NS(id=call_id, type="function", function=NS(name=name, arguments=arguments))


def add(a, b):
    return a + b


def boom():
    raise RuntimeError("it broke")


FUNCTIONS = {"add": add, "boom": boom}


def test_runs_the_function():
    assert run_tool_call(make_call("add", '{"a": 2, "b": 3}'), FUNCTIONS) == {
        "role": "tool",
        "tool_call_id": "c1",
        "content": "5",
    }


def test_content_is_always_text():
    result = run_tool_call(make_call("add", '{"a": 1.5, "b": 1}', "c9"), FUNCTIONS)
    assert result["content"] == "2.5" and result["tool_call_id"] == "c9"


def test_unknown_tool():
    result = run_tool_call(make_call("fly", "{}"), FUNCTIONS)
    assert result["content"] == "error: unknown tool fly"
    assert result["role"] == "tool" and result["tool_call_id"] == "c1"


def test_invalid_arguments():
    assert run_tool_call(make_call("add", "not json"), FUNCTIONS)["content"] == "error: invalid arguments"
    assert run_tool_call(make_call("add", "[1, 2]"), FUNCTIONS)["content"] == "error: invalid arguments"


def test_function_errors():
    assert run_tool_call(make_call("boom", "{}"), FUNCTIONS)["content"] == "error: it broke"
    wrong_args = run_tool_call(make_call("add", '{"a": 1}'), FUNCTIONS)["content"]
    assert wrong_args.startswith("error: "), "a missing argument raises TypeError, which becomes an error message"
