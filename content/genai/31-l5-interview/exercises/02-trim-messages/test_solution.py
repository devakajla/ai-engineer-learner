from solution import estimate_tokens, trim_messages


def msg(role, tokens):
    return {"role": role, "content": "x" * (tokens * 4)}


def test_keeps_system_and_newest():
    msgs = [msg("system", 8), msg("user", 4), msg("assistant", 4), msg("user", 4)]
    assert trim_messages(msgs, 16) == [msgs[0], msgs[2], msgs[3]]
    assert trim_messages(msgs, 12) == [msgs[0], msgs[3]]


def test_everything_fits():
    msgs = [msg("system", 1), msg("user", 1)]
    assert trim_messages(msgs, 100) == msgs


def test_no_system_message():
    msgs = [msg("user", 4), msg("assistant", 4), msg("user", 4)]
    assert trim_messages(msgs, 8) == msgs[1:]


def test_stops_at_first_miss_going_back():
    msgs = [msg("user", 1), msg("assistant", 10), msg("user", 2)]
    assert trim_messages(msgs, 5) == [msgs[2]], "must not skip the big one to keep the old small one"


def test_system_alone_when_too_big():
    msgs = [msg("system", 50), msg("user", 1)]
    assert trim_messages(msgs, 10) == [msgs[0]]


def test_none_content_and_empty():
    assert trim_messages([], 10) == []
    msgs = [{"role": "assistant", "content": None}, msg("user", 2)]
    assert trim_messages(msgs, 2) == msgs


def test_input_not_changed():
    msgs = [msg("system", 2), msg("user", 5), msg("user", 1)]
    before = list(msgs)
    trim_messages(msgs, 3)
    assert msgs == before
