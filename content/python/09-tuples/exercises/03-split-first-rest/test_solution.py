from solution import split_first


def test_examples():
    assert split_first([1, 2, 3]) == (1, [2, 3])
    assert split_first(["x"]) == ("x", [])
    assert split_first([]) == (None, [])


def test_more():
    assert split_first((5, 6)) == (5, [6]), "rest must be a list, even for a tuple input"
    first, rest = split_first("abc")
    assert first == "a" and rest == ["b", "c"]
