from solution import parse_react


def test_action():
    text = 'Thought: x\nAction: add\nAction Input: {"a": 1, "b": 2}'
    assert parse_react(text) == {"type": "action", "tool": "add", "args": {"a": 1, "b": 2}}


def test_final():
    assert parse_react("Thought: done\nFinal Answer: 42") == {"type": "final", "answer": "42"}


def test_final_multiline():
    out = parse_react("Final Answer: line one\nline two\n")
    assert out == {"type": "final", "answer": "line one\nline two"}


def test_no_action():
    assert parse_react("Thought: hmm") == {"type": "error", "reason": "no action"}
    assert parse_react("") == {"type": "error", "reason": "no action"}
    assert parse_react("Action:   \nAction Input: {}") == {"type": "error", "reason": "no action"}


def test_missing_input_means_empty_args():
    assert parse_react("Action: ping") == {"type": "action", "tool": "ping", "args": {}}


def test_bad_arguments():
    assert parse_react("Action: add\nAction Input: {a: 1}") == {"type": "error", "reason": "bad arguments"}
    assert parse_react("Action: add\nAction Input: [1, 2]") == {"type": "error", "reason": "bad arguments"}


def test_first_marker_wins():
    assert parse_react("Final Answer: ok\nAction: add")["type"] == "final"
    assert parse_react('Action: add\nAction Input: {}\nFinal Answer: ok')["type"] == "action"


def test_indented_lines():
    out = parse_react('   Action: add\n   Action Input: {"a": 1}')
    assert out == {"type": "action", "tool": "add", "args": {"a": 1}}
