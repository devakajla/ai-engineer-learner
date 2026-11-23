from solution import row_col_sums


def test_examples():
    assert row_col_sums([[1, 2, 3], [4, 5, 6]]) == ([6, 15], [5, 7, 9])


def test_more():
    assert row_col_sums([[5]]) == ([5], [5])
    assert row_col_sums([[1], [2], [3]]) == ([1, 2, 3], [6])
    assert row_col_sums([[0, 0], [0, 0]]) == ([0, 0], [0, 0])
