import json

from solution import check_example, to_jsonl_line


def test_line_has_system_user_assistant():
    line = to_jsonl_line("Be short.", "Hi", "Hello!")
    assert json.loads(line) == {
        "messages": [
            {"role": "system", "content": "Be short."},
            {"role": "user", "content": "Hi"},
            {"role": "assistant", "content": "Hello!"},
        ]
    }
    assert "\n" not in line, "one example per line"


def test_no_system_message_when_empty():
    for system in (None, ""):
        roles = [m["role"] for m in json.loads(to_jsonl_line(system, "Hi", "Hello"))["messages"]]
        assert roles == ["user", "assistant"]


def test_good_example_has_no_problems():
    assert check_example(to_jsonl_line("s", "q", "a")) == []


def test_bad_json():
    assert check_example("{oops") == ["not valid JSON"]


def test_missing_messages():
    assert check_example('{"text": "hi"}') == ["no messages list"]
    assert check_example("[]") == ["no messages list"]
    assert check_example('{"messages": []}') == ["no messages list"]


def test_wrong_last_role_and_missing_user():
    line = json.dumps({"messages": [{"role": "assistant", "content": "x"}, {"role": "user", "content": "y"}]})
    assert check_example(line) == ["last message must be from the assistant"]
    line = json.dumps({"messages": [{"role": "system", "content": "x"}, {"role": "assistant", "content": "y"}]})
    assert check_example(line) == ["no user message"]


def test_empty_content_is_reported():
    line = json.dumps({"messages": [{"role": "user", "content": " "}, {"role": "assistant", "content": "ok"}]})
    assert check_example(line) == ["empty user message"]
