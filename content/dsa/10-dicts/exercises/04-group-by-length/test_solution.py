from solution import group_by_length


def test_examples():
    assert group_by_length(["hi", "yo", "hey"]) == {2: ["hi", "yo"], 3: ["hey"]}


def test_more():
    assert group_by_length([]) == {}
    assert group_by_length(["a", "b", "a"]) == {1: ["a", "b", "a"]}
    assert group_by_length(["abc", "de", "fgh", "i"]) == {3: ["abc", "fgh"], 2: ["de"], 1: ["i"]}
