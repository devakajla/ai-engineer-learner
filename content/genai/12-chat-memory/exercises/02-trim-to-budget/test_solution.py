from solution import trim_to_budget


def msg(role, size):
    return {"role": role, "content": "x" * size}


H = [msg("user", 12), msg("assistant", 16), msg("user", 8), msg("assistant", 8)]   # 3, 4, 2, 2 tokens


def test_examples():
    assert trim_to_budget(H, 5) == H[2:], "the last two messages cost 2 + 2 = 4"
    assert trim_to_budget(H, 100) == H
    assert trim_to_budget(H, 1) == []


def test_stops_at_first_message_that_does_not_fit():
    h = [msg("user", 4), msg("assistant", 40), msg("user", 4)]   # 1, 10, 1 tokens
    assert trim_to_budget(h, 5) == [h[2]], "do not skip the big message to keep the older small one"


def test_exact_fit_and_order():
    assert trim_to_budget(H, 4) == H[2:], "a total equal to the budget is allowed"
    assert trim_to_budget(H, 6) == H[2:], "adding the 4-token message would make 8 > 6"
    assert trim_to_budget(H, 8) == H[1:], "4 + 2 + 2 = 8 fits; keep the original order"


def test_edges_and_no_change():
    assert trim_to_budget([], 10) == []
    assert trim_to_budget(H, 0) == []
    before = list(H)
    trim_to_budget(H, 5)
    assert H == before, "do not change the list that was passed in"
