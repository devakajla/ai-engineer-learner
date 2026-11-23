from solution import group_by_length


def test_examples():
    assert group_by_length(["hi", "yo", "hello", "hey"]) == {2: ["hi", "yo"], 5: ["hello"], 3: ["hey"]}
    assert group_by_length([]) == {}


def test_more():
    assert group_by_length(["a", "b", "a"]) == {1: ["a", "b", "a"]}, "keep duplicates and order"
    assert list(group_by_length(["abc", "a"]).keys()) == [3, 1], "keys in first-seen order"
