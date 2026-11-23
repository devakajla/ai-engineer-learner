from solution import move_zeros


def test_examples():
    assert move_zeros([0, 1, 0, 3, 12]) == [1, 3, 12, 0, 0]
    assert move_zeros([0, 0]) == [0, 0]


def test_more():
    assert move_zeros([]) == []
    assert move_zeros([1, 2, 3]) == [1, 2, 3]
    assert move_zeros([4, 0]) == [4, 0]
    assert move_zeros([0, -1]) == [-1, 0]
