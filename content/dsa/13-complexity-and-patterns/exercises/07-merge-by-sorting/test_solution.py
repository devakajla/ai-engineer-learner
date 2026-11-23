from solution import merge_sorted


def test_examples():
    assert merge_sorted([1, 3, 5], [2, 4, 6]) == [1, 2, 3, 4, 5, 6]
    assert merge_sorted([], [1]) == [1]


def test_edges():
    assert merge_sorted([], []) == []
    assert merge_sorted([1, 1], [1]) == [1, 1, 1]
    assert merge_sorted([-3, 0], [-5, 4, 9]) == [-5, -3, 0, 4, 9]


def test_inputs_not_changed():
    a, b = [1, 4], [2, 3]
    merge_sorted(a, b)
    assert a == [1, 4] and b == [2, 3], "do not modify the input lists"
