from solution import safe_tool_call


def tool(name, props=None, required=None):
    return {"type": "function", "function": {"name": name, "description": "does " + name, "parameters": {
        "type": "object", "properties": props or {}, "required": required or []}}}


INT2 = {"a": {"type": "integer", "description": "x"}, "b": {"type": "integer", "description": "y"}}
TOOLS = [tool("div", INT2, ["a", "b"]), tool("add", INT2, ["a", "b"]), tool("text", {"n": {"type": "integer", "description": "n"}}, ["n"])]


def add(a, b):
    return a + b


def div(a, b):
    return a / b


def text(n):
    return "x" * n


FUNCTIONS = {"add": add, "div": div, "text": text}


def test_normal_call_returns_text():
    assert safe_tool_call(TOOLS, FUNCTIONS, "add", {"a": 1, "b": 2}) == "3"
    assert safe_tool_call(TOOLS, FUNCTIONS, "div", {"a": 1, "b": 4}) == "0.25"


def test_unknown_tool_lists_the_sorted_names():
    assert safe_tool_call(TOOLS, FUNCTIONS, "sub", {}) == "error: unknown tool sub. Available tools: add, div, text"
    assert safe_tool_call([], {}, "sub", {}) == "error: unknown tool sub. Available tools: (none)"


def test_tool_without_a_function_is_unknown():
    assert safe_tool_call(TOOLS, {"add": add}, "div", {"a": 1, "b": 1}).startswith("error: unknown tool div")


def test_bad_arguments_do_not_call_the_function():
    calls = []

    def spy(a, b):
        calls.append((a, b))
        return 0

    out = safe_tool_call([tool("spy", INT2, ["a", "b"])], {"spy": spy}, "spy", {"a": "1"})
    assert out == "error: missing required argument b; argument a must be integer"
    assert calls == [], "the function must not run with bad arguments"


def test_exceptions_become_text():
    assert safe_tool_call(TOOLS, FUNCTIONS, "div", {"a": 1, "b": 0}) == "error: ZeroDivisionError: division by zero"


def test_long_results_are_cut():
    out = safe_tool_call(TOOLS, FUNCTIONS, "text", {"n": 30}, max_chars=10)
    assert out == "x" * 10 + "\n[truncated 20 more characters]"
    assert safe_tool_call(TOOLS, FUNCTIONS, "text", {"n": 30}) == "x" * 30


def test_a_non_string_result_is_turned_into_text():
    assert safe_tool_call(TOOLS, FUNCTIONS, "add", {"a": 2, "b": 2}) == "4"
