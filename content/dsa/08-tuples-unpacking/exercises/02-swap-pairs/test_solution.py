from solution import swap_pairs


def test_examples():
    assert swap_pairs([1, 2, 3, 4]) == [2, 1, 4, 3]
    assert swap_pairs([1, 2, 3]) == [2, 1, 3]


def test_more():
    assert swap_pairs([]) == []
    assert swap_pairs([9]) == [9]
    original = [1, 2]
    swap_pairs(original)
    assert original == [1, 2], "do not change the input list"
