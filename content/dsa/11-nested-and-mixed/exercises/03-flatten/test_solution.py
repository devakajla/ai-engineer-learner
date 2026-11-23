from solution import flatten


def test_examples():
    assert flatten([[1, 2], [3], [4, 5]]) == [1, 2, 3, 4, 5]
    assert flatten([[], [1], []]) == [1]


def test_more():
    assert flatten([]) == []
    assert flatten([["a"], ["b", "c"]]) == ["a", "b", "c"]
