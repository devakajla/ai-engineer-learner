from solution import merge_sorted


def test_examples():
    assert merge_sorted([1, 3, 5], [2, 4, 6]) == [1, 2, 3, 4, 5, 6]
    assert merge_sorted([], [1, 2]) == [1, 2]
    assert merge_sorted([1, 1], [1]) == [1, 1, 1]


def test_more():
    assert merge_sorted([], []) == []
    assert merge_sorted([5, 6], [1, 2]) == [1, 2, 5, 6]
    assert merge_sorted([1, 2, 3], [4]) == [1, 2, 3, 4]
    assert merge_sorted([-3, 0], [-2, 5]) == [-3, -2, 0, 5]


def test_no_sort_calls():
    import builtins
    calls = []
    real_sorted = builtins.sorted
    builtins.sorted = lambda *a, **k: (calls.append(1), real_sorted(*a, **k))[1]
    try:
        merge_sorted([1, 3], [2, 4])
    finally:
        builtins.sorted = real_sorted
    assert not calls, "do not use sorted(); use two indexes"
