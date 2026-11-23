from solution import trim_last


def test_examples():
    h = ["a", "b", "c", "d"]
    assert trim_last(h, 2) == ["c", "d"]
    assert trim_last(h, 10) == ["a", "b", "c", "d"]
    assert trim_last(h, 0) == [], "n = 0 must give an empty list (h[-0:] would give everything)"


def test_edges():
    assert trim_last([], 3) == []
    assert trim_last(["a"], 1) == ["a"]
    assert trim_last(["a", "b"], -2) == [], "a negative n gives an empty list"
    assert trim_last(["a", "b", "c"], 3) == ["a", "b", "c"]


def test_returns_a_new_list():
    h = ["a", "b", "c"]
    result = trim_last(h, 3)
    result.append("x")
    assert h == ["a", "b", "c"], "do not change or share the original list"
    messages = [{"role": "user", "content": "hi"}]
    assert trim_last(messages, 1) == messages
