from solution import trim_messages


def msg(role, size):
    return {"role": role, "content": "x" * size}


M = [msg("system", 8), msg("user", 20), msg("assistant", 8), msg("user", 8)]   # 2, 5, 2, 2 tokens


def test_examples():
    assert trim_messages(M, 6) == [M[0], M[2], M[3]]
    assert trim_messages(M, 2) == [M[0]], "the system message is always kept"
    assert trim_messages(M, 100) == M


def test_system_tokens_count():
    assert trim_messages(M, 5) == [M[0], M[3]], "2 (system) + 2 = 4 fits, but another 2 would make 6 > 5"


def test_system_is_kept_even_if_too_big():
    assert trim_messages(M, 0) == [M[0]]
    assert trim_messages(M, 1) == [M[0]]


def test_no_system_message():
    rest = M[1:]
    assert trim_messages(rest, 4) == rest[1:], "2 + 2 = 4 fits, adding the 5-token message does not"
    assert trim_messages(rest, 0) == []
    assert trim_messages([], 10) == []


def test_stops_at_first_misfit_and_does_not_change_input():
    h = [msg("system", 4), msg("user", 4), msg("assistant", 40), msg("user", 4)]   # 1, 1, 10, 1
    assert trim_messages(h, 5) == [h[0], h[3]], "do not skip the 10-token message to keep the older small one"
    before = list(h)
    trim_messages(h, 5)
    assert h == before
